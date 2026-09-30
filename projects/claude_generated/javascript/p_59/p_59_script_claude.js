const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');
const express = require('express');
const path = require('path');

/**
 * Log Aggregator Service
 * Aggregates logs from multiple sources with various transports
 */
class LogAggregator {
  constructor(config = {}) {
    this.config = {
      logDir: config.logDir || './logs',
      maxSize: config.maxSize || '10m',
      maxFiles: config.maxFiles || '14d',
      httpPort: config.httpPort || 3000,
      ...config
    };

    this.loggers = new Map();
    this.httpServer = null;
    this.initializeDefaultLogger();
  }

  /**
   * Initialize the default logger with all transports
   */
  initializeDefaultLogger() {
    const defaultLogger = this.createLogger('default', {
      level: 'info',
      enableConsole: true,
      enableFile: true,
      enableHttp: false
    });

    this.loggers.set('default', defaultLogger);
  }

  /**
   * Create a custom format for logs
   */
  getLogFormat() {
    return winston.format.combine(
      winston.format.timestamp({
        format: 'YYYY-MM-DD HH:mm:ss'
      }),
      winston.format.errors({ stack: true }),
      winston.format.splat(),
      winston.format.json(),
      winston.format.printf(({ timestamp, level, message, source, ...metadata }) => {
        let msg = `${timestamp} [${level.toUpperCase()}]`;

        if (source) {
          msg += ` [${source}]`;
        }

        msg += `: ${message}`;

        if (Object.keys(metadata).length > 0) {
          msg += ` ${JSON.stringify(metadata)}`;
        }

        return msg;
      })
    );
  }

  /**
   * Create a logger for a specific source
   */
  createLogger(sourceName, options = {}) {
    const {
      level = 'info',
      enableConsole = true,
      enableFile = true,
      enableHttp = false,
      httpEndpoint = null
    } = options;

    const transports = [];

    // Console Transport
    if (enableConsole) {
      transports.push(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.printf(({ timestamp, level, message, source }) => {
              return `${timestamp} [${level}] [${source || sourceName}]: ${message}`;
            })
          )
        })
      );
    }

    // File Transport with Rotation (Combined logs)
    if (enableFile) {
      transports.push(
        new DailyRotateFile({
          filename: path.join(this.config.logDir, `${sourceName}-%DATE%-combined.log`),
          datePattern: 'YYYY-MM-DD',
          maxSize: this.config.maxSize,
          maxFiles: this.config.maxFiles,
          format: this.getLogFormat()
        })
      );

      // Error-only file transport
      transports.push(
        new DailyRotateFile({
          filename: path.join(this.config.logDir, `${sourceName}-%DATE%-error.log`),
          datePattern: 'YYYY-MM-DD',
          maxSize: this.config.maxSize,
          maxFiles: this.config.maxFiles,
          level: 'error',
          format: this.getLogFormat()
        })
      );
    }

    // HTTP Transport (for remote logging)
    if (enableHttp && httpEndpoint) {
      transports.push(
        new winston.transports.Http({
          host: httpEndpoint.host || 'localhost',
          port: httpEndpoint.port || 3000,
          path: httpEndpoint.path || '/logs'
        })
      );
    }

    const logger = winston.createLogger({
      level,
      format: this.getLogFormat(),
      defaultMeta: { source: sourceName },
      transports
    });

    return logger;
  }

  /**
   * Register a new log source
   */
  registerSource(sourceName, options = {}) {
    if (this.loggers.has(sourceName)) {
      console.warn(`Logger for source "${sourceName}" already exists. Overwriting...`);
    }

    const logger = this.createLogger(sourceName, options);
    this.loggers.set(sourceName, logger);

    return logger;
  }

  /**
   * Get logger for a specific source
   */
  getLogger(sourceName = 'default') {
    if (!this.loggers.has(sourceName)) {
      console.warn(`Logger for source "${sourceName}" not found. Using default logger.`);
      return this.loggers.get('default');
    }

    return this.loggers.get(sourceName);
  }

  /**
   * Log a message to a specific source
   */
  log(sourceName, level, message, metadata = {}) {
    const logger = this.getLogger(sourceName);
    logger.log(level, message, metadata);
  }

  /**
   * Start HTTP server to receive logs from remote sources
   */
  startHttpServer(port = this.config.httpPort) {
    const app = express();
    app.use(express.json());

    // Endpoint to receive logs
    app.post('/logs', (req, res) => {
      const { source, level, message, metadata } = req.body;

      if (!source || !level || !message) {
        return res.status(400).json({
          error: 'Missing required fields: source, level, message'
        });
      }

      this.log(source, level, message, metadata || {});

      res.status(200).json({
        success: true,
        message: 'Log received'
      });
    });

    // Endpoint to register new log sources
    app.post('/sources', (req, res) => {
      const { name, options } = req.body;

      if (!name) {
        return res.status(400).json({
          error: 'Missing required field: name'
        });
      }

      this.registerSource(name, options || {});

      res.status(201).json({
        success: true,
        message: `Source "${name}" registered`
      });
    });

    // Endpoint to list all sources
    app.get('/sources', (req, res) => {
      const sources = Array.from(this.loggers.keys());
      res.status(200).json({ sources });
    });

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.status(200).json({
        status: 'healthy',
        sources: this.loggers.size
      });
    });

    this.httpServer = app.listen(port, () => {
      console.log(`Log Aggregator HTTP server listening on port ${port}`);
    });

    return this.httpServer;
  }

  /**
   * Stop HTTP server
   */
  stopHttpServer() {
    if (this.httpServer) {
      this.httpServer.close(() => {
        console.log('Log Aggregator HTTP server stopped');
      });
    }
  }

  /**
   * Close all loggers
   */
  closeAll() {
    this.loggers.forEach((logger, name) => {
      logger.close();
      console.log(`Closed logger: ${name}`);
    });

    this.stopHttpServer();
  }
}

module.exports = LogAggregator;

// If running directly, start the service
if (require.main === module) {
  const aggregator = new LogAggregator({
    logDir: './logs',
    maxSize: '10m',
    maxFiles: '14d',
    httpPort: 3000
  });

  // Register multiple sources
  aggregator.registerSource('application', {
    level: 'debug',
    enableConsole: true,
    enableFile: true
  });

  aggregator.registerSource('database', {
    level: 'info',
    enableConsole: true,
    enableFile: true
  });

  aggregator.registerSource('api', {
    level: 'info',
    enableConsole: true,
    enableFile: true
  });

  // Start HTTP server for remote logging
  aggregator.startHttpServer();

  // Example logs
  aggregator.log('application', 'info', 'Application started successfully');
  aggregator.log('database', 'info', 'Connected to database', { host: 'localhost', port: 5432 });
  aggregator.log('api', 'warn', 'API rate limit approaching', { limit: 1000, current: 950 });
  aggregator.log('application', 'error', 'Failed to process request', {
    error: 'Timeout',
    duration: 5000
  });

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\nShutting down gracefully...');
    aggregator.closeAll();
    process.exit(0);
  });
}
