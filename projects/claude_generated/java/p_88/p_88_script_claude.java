package com.example.logging;

import ch.qos.logback.classic.*;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.*;
import ch.qos.logback.core.rolling.*;
import net.logstash.logback.encoder.LogstashEncoder;
import org.slf4j.*;

import java.util.*;

class LoggingManager {
    private final LoggerContext loggerContext;

    public LoggingManager() {
        this.loggerContext = (LoggerContext) LoggerFactory.getILoggerFactory();
    }

    public void configureConsoleAppender(String pattern, Level level) {
        Logger rootLogger = loggerContext.getLogger(Logger.ROOT_LOGGER_NAME);

        // Create console appender
        ConsoleAppender<ILoggingEvent> consoleAppender = new ConsoleAppender<>();
        consoleAppender.setContext(loggerContext);
        consoleAppender.setName("CONSOLE");

        // Create pattern encoder
        PatternLayoutEncoder encoder = new PatternLayoutEncoder();
        encoder.setContext(loggerContext);
        encoder.setPattern(pattern);
        encoder.start();

        consoleAppender.setEncoder(encoder);
        consoleAppender.start();

        rootLogger.addAppender(consoleAppender);
        rootLogger.setLevel(level);
    }

    public void configureFileAppender(String fileName, String pattern, Level level) {
        Logger rootLogger = loggerContext.getLogger(Logger.ROOT_LOGGER_NAME);

        // Create file appender
        FileAppender<ILoggingEvent> fileAppender = new FileAppender<>();
        fileAppender.setContext(loggerContext);
        fileAppender.setName("FILE");
        fileAppender.setFile(fileName);

        // Create pattern encoder
        PatternLayoutEncoder encoder = new PatternLayoutEncoder();
        encoder.setContext(loggerContext);
        encoder.setPattern(pattern);
        encoder.start();

        fileAppender.setEncoder(encoder);
        fileAppender.start();

        rootLogger.addAppender(fileAppender);
        rootLogger.setLevel(level);
    }

    public void configureRollingFileAppender(String filePattern, Level level) {
        Logger rootLogger = loggerContext.getLogger(Logger.ROOT_LOGGER_NAME);

        // Create rolling file appender
        RollingFileAppender<ILoggingEvent> rollingAppender = new RollingFileAppender<>();
        rollingAppender.setContext(loggerContext);
        rollingAppender.setName("ROLLING-FILE");
        rollingAppender.setFile("logs/application.log");

        // Time-based rolling policy
        TimeBasedRollingPolicy<ILoggingEvent> rollingPolicy = new TimeBasedRollingPolicy<>();
        rollingPolicy.setContext(loggerContext);
        rollingPolicy.setParent(rollingAppender);
        rollingPolicy.setFileNamePattern(filePattern);
        rollingPolicy.setMaxHistory(30); // Keep 30 days
        rollingPolicy.start();

        // Size and time based rolling policy
        SizeAndTimeBasedRollingPolicy<ILoggingEvent> sizePolicy =
            new SizeAndTimeBasedRollingPolicy<>();
        sizePolicy.setContext(loggerContext);
        sizePolicy.setParent(rollingAppender);
        sizePolicy.setFileNamePattern("logs/application-%d{yyyy-MM-dd}-%i.log");
        sizePolicy.setMaxFileSize(FileSize.valueOf("10MB"));
        sizePolicy.setMaxHistory(30);
        sizePolicy.setTotalSizeCap(FileSize.valueOf("1GB"));
        sizePolicy.start();

        // Create pattern encoder
        PatternLayoutEncoder encoder = new PatternLayoutEncoder();
        encoder.setContext(loggerContext);
        encoder.setPattern("%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n");
        encoder.start();

        rollingAppender.setRollingPolicy(sizePolicy);
        rollingAppender.setEncoder(encoder);
        rollingAppender.start();

        rootLogger.addAppender(rollingAppender);
        rootLogger.setLevel(level);
    }

    public void configureJsonLogging(String fileName) {
        Logger rootLogger = loggerContext.getLogger(Logger.ROOT_LOGGER_NAME);

        // Create file appender with JSON encoder
        FileAppender<ILoggingEvent> jsonAppender = new FileAppender<>();
        jsonAppender.setContext(loggerContext);
        jsonAppender.setName("JSON-FILE");
        jsonAppender.setFile(fileName);

        // Use Logstash JSON encoder
        LogstashEncoder encoder = new LogstashEncoder();
        encoder.setContext(loggerContext);
        encoder.start();

        jsonAppender.setEncoder(encoder);
        jsonAppender.start();

        rootLogger.addAppender(jsonAppender);
    }

    public void setLogLevel(String loggerName, Level level) {
        Logger logger = loggerContext.getLogger(loggerName);
        logger.setLevel(level);
    }

    public void clearAppenders() {
        Logger rootLogger = loggerContext.getLogger(Logger.ROOT_LOGGER_NAME);
        rootLogger.detachAndStopAllAppenders();
    }
}

class StructuredLogger {
    private final Logger logger;

    public StructuredLogger(Class<?> clazz) {
        this.logger = LoggerFactory.getLogger(clazz);
    }

    public void logWithContext(String message, Map<String, String> context) {
        // Add context to MDC
        context.forEach(MDC::put);

        try {
            logger.info(message);
        } finally {
            // Clear MDC
            context.keySet().forEach(key -> MDC.remove(key));
        }
    }

    public void logError(String message, Throwable exception, Map<String, String> context) {
        context.forEach(MDC::put);

        try {
            logger.error(message, exception);
        } finally {
            context.keySet().forEach(key -> MDC.remove(key));
        }
    }

    public Logger getLogger() {
        return logger;
    }
}

class AuditLogger {
    private final Logger logger;
    private final Marker auditMarker;

    public AuditLogger() {
        this.logger = LoggerFactory.getLogger("AUDIT");
        this.auditMarker = MarkerFactory.getMarker("AUDIT");
    }

    public void logUserAction(String userId, String action, String resource, String result) {
        Map<String, String> context = new HashMap<>();
        context.put("userId", userId);
        context.put("action", action);
        context.put("resource", resource);
        context.put("result", result);
        context.put("timestamp", String.valueOf(System.currentTimeMillis()));

        context.forEach(MDC::put);

        try {
            logger.info(auditMarker, "User action: {} on {} - {}", action, resource, result);
        } finally {
            context.keySet().forEach(key -> MDC.remove(key));
        }
    }

    public void logSecurityEvent(String eventType, String description, String severity) {
        Map<String, String> context = new HashMap<>();
        context.put("eventType", eventType);
        context.put("severity", severity);
        context.put("timestamp", String.valueOf(System.currentTimeMillis()));

        context.forEach(MDC::put);

        try {
            logger.warn(auditMarker, "Security event: {} - {}", eventType, description);
        } finally {
            context.keySet().forEach(key -> MDC.remove(key));
        }
    }
}

class PerformanceLogger {
    private final Logger logger;
    private final Map<String, Long> timers;

    public PerformanceLogger(Class<?> clazz) {
        this.logger = LoggerFactory.getLogger(clazz);
        this.timers = new HashMap<>();
    }

    public void startTimer(String operation) {
        timers.put(operation, System.currentTimeMillis());
    }

    public void endTimer(String operation) {
        Long startTime = timers.get(operation);
        if (startTime != null) {
            long duration = System.currentTimeMillis() - startTime;
            MDC.put("duration_ms", String.valueOf(duration));
            MDC.put("operation", operation);

            try {
                if (duration > 1000) {
                    logger.warn("Slow operation: {} took {}ms", operation, duration);
                } else {
                    logger.debug("Operation: {} completed in {}ms", operation, duration);
                }
            } finally {
                MDC.remove("duration_ms");
                MDC.remove("operation");
            }

            timers.remove(operation);
        }
    }

    public <T> T measureExecution(String operation, java.util.function.Supplier<T> supplier) {
        startTimer(operation);
        try {
            return supplier.get();
        } finally {
            endTimer(operation);
        }
    }
}

class BusinessLogger {
    private final StructuredLogger logger;

    public BusinessLogger(Class<?> clazz) {
        this.logger = new StructuredLogger(clazz);
    }

    public void logOrderCreated(String orderId, String customerId, double amount) {
        Map<String, String> context = new HashMap<>();
        context.put("orderId", orderId);
        context.put("customerId", customerId);
        context.put("amount", String.valueOf(amount));
        context.put("eventType", "ORDER_CREATED");

        logger.logWithContext("Order created successfully", context);
    }

    public void logPaymentProcessed(String paymentId, String orderId, String status) {
        Map<String, String> context = new HashMap<>();
        context.put("paymentId", paymentId);
        context.put("orderId", orderId);
        context.put("status", status);
        context.put("eventType", "PAYMENT_PROCESSED");

        logger.logWithContext("Payment processed", context);
    }

    public void logBusinessError(String operation, String errorCode, String message) {
        Map<String, String> context = new HashMap<>();
        context.put("operation", operation);
        context.put("errorCode", errorCode);
        context.put("eventType", "BUSINESS_ERROR");

        logger.logError(message, new Exception(message), context);
    }
}

public class LoggingFramework {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Advanced Logging Framework Demo ===\n");

        // Initialize logging manager
        LoggingManager loggingManager = new LoggingManager();

        // Configure console logging with colored output
        String colorPattern = "%d{HH:mm:ss.SSS} [%thread] %highlight(%-5level) " +
                            "%cyan(%logger{36}) - %msg%n";
        loggingManager.configureConsoleAppender(colorPattern, Level.DEBUG);

        // Configure file logging
        loggingManager.configureFileAppender(
            "logs/application.log",
            "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n",
            Level.INFO
        );

        // Configure JSON logging
        loggingManager.configureJsonLogging("logs/application.json");

        // Example 1: Basic logging
        System.out.println("--- Example 1: Basic Logging Levels ---");
        Logger basicLogger = LoggerFactory.getLogger(LoggingFramework.class);
        basicLogger.trace("This is a TRACE message");
        basicLogger.debug("This is a DEBUG message");
        basicLogger.info("This is an INFO message");
        basicLogger.warn("This is a WARN message");
        basicLogger.error("This is an ERROR message");

        // Example 2: Structured logging with context
        System.out.println("\n--- Example 2: Structured Logging with MDC ---");
        StructuredLogger structuredLogger = new StructuredLogger(LoggingFramework.class);

        Map<String, String> context = new HashMap<>();
        context.put("userId", "user123");
        context.put("sessionId", "session-abc-456");
        context.put("ipAddress", "192.168.1.100");

        structuredLogger.logWithContext("User logged in successfully", context);

        // Example 3: Audit logging
        System.out.println("\n--- Example 3: Audit Logging ---");
        AuditLogger auditLogger = new AuditLogger();

        auditLogger.logUserAction("user123", "CREATE", "/api/orders", "SUCCESS");
        auditLogger.logUserAction("user456", "DELETE", "/api/users/789", "SUCCESS");
        auditLogger.logSecurityEvent("FAILED_LOGIN_ATTEMPT",
            "Multiple failed login attempts detected", "HIGH");

        // Example 4: Performance logging
        System.out.println("\n--- Example 4: Performance Logging ---");
        PerformanceLogger perfLogger = new PerformanceLogger(LoggingFramework.class);

        perfLogger.startTimer("database-query");
        Thread.sleep(150); // Simulate database query
        perfLogger.endTimer("database-query");

        // Using measure execution
        String result = perfLogger.measureExecution("api-call", () -> {
            try {
                Thread.sleep(250); // Simulate API call
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "API Response";
        });
        System.out.println("API call result: " + result);

        // Slow operation warning
        perfLogger.startTimer("slow-operation");
        Thread.sleep(1200); // Simulate slow operation
        perfLogger.endTimer("slow-operation");

        // Example 5: Business event logging
        System.out.println("\n--- Example 5: Business Event Logging ---");
        BusinessLogger businessLogger = new BusinessLogger(LoggingFramework.class);

        businessLogger.logOrderCreated("ORD-123", "CUST-456", 299.99);
        businessLogger.logPaymentProcessed("PAY-789", "ORD-123", "COMPLETED");
        businessLogger.logBusinessError("ORDER_PROCESSING", "INV_001",
            "Insufficient inventory for product");

        // Example 6: Exception logging
        System.out.println("\n--- Example 6: Exception Logging ---");
        try {
            throw new IllegalArgumentException("Invalid parameter provided");
        } catch (Exception e) {
            Map<String, String> errorContext = new HashMap<>();
            errorContext.put("errorType", e.getClass().getSimpleName());
            errorContext.put("operation", "data-validation");

            structuredLogger.logError("Operation failed due to validation error", e, errorContext);
        }

        // Example 7: Dynamic log level changes
        System.out.println("\n--- Example 7: Dynamic Log Level Changes ---");
        Logger testLogger = LoggerFactory.getLogger("com.example.test");

        loggingManager.setLogLevel("com.example.test", Level.DEBUG);
        testLogger.debug("This DEBUG message will be shown");

        loggingManager.setLogLevel("com.example.test", Level.WARN);
        testLogger.debug("This DEBUG message will NOT be shown");
        testLogger.warn("This WARN message will be shown");

        System.out.println("\n=== Logging Framework Demo Complete ===");
        System.out.println("Check the logs/ directory for output files:");
        System.out.println("  - logs/application.log (text format)");
        System.out.println("  - logs/application.json (JSON format)");
    }
}
