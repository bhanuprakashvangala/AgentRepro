import chokidar from 'chokidar';

/**
 * FileWatcher class with debouncing support
 */
class FileWatcher {
  constructor(options = {}) {
    this.watchPaths = options.paths || ['./'];
    this.debounceDelay = options.debounceDelay || 300;
    this.chokidarOptions = {
      ignored: options.ignored || /(^|[\/\\])\../,
      persistent: true,
      ignoreInitial: options.ignoreInitial !== false,
      awaitWriteFinish: {
        stabilityThreshold: 100,
        pollInterval: 100
      },
      ...options.chokidarOptions
    };

    this.callbacks = {
      add: [],
      change: [],
      unlink: [],
      addDir: [],
      unlinkDir: [],
      error: [],
      ready: []
    };

    this.debounceTimers = new Map();
    this.watcher = null;
  }

  /**
   * Register a callback for specific event
   * @param {string} event - Event type (add, change, unlink, addDir, unlinkDir, error, ready)
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    if (this.callbacks[event]) {
      this.callbacks[event].push(callback);
    } else {
      console.warn(`Unknown event: ${event}`);
    }
    return this;
  }

  /**
   * Debounced event trigger
   * @param {string} event - Event type
   * @param {string} path - File path
   * @param {*} stats - File stats (optional)
   */
  _triggerDebounced(event, path, stats) {
    const key = `${event}:${path}`;

    // Clear existing timer for this path
    if (this.debounceTimers.has(key)) {
      clearTimeout(this.debounceTimers.get(key));
    }

    // Set new timer
    const timer = setTimeout(() => {
      this.callbacks[event].forEach(callback => {
        try {
          callback(path, stats);
        } catch (error) {
          console.error(`Error in ${event} callback:`, error);
        }
      });
      this.debounceTimers.delete(key);
    }, this.debounceDelay);

    this.debounceTimers.set(key, timer);
  }

  /**
   * Immediate event trigger (no debouncing)
   * @param {string} event - Event type
   * @param {*} data - Event data
   */
  _triggerImmediate(event, data) {
    this.callbacks[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in ${event} callback:`, error);
      }
    });
  }

  /**
   * Start watching
   */
  start() {
    if (this.watcher) {
      console.warn('Watcher already started');
      return this;
    }

    console.log(`Starting file watcher on: ${this.watchPaths.join(', ')}`);

    this.watcher = chokidar.watch(this.watchPaths, this.chokidarOptions);

    // File added
    this.watcher.on('add', (path, stats) => {
      this._triggerDebounced('add', path, stats);
    });

    // File changed
    this.watcher.on('change', (path, stats) => {
      this._triggerDebounced('change', path, stats);
    });

    // File deleted
    this.watcher.on('unlink', (path) => {
      this._triggerDebounced('unlink', path);
    });

    // Directory added
    this.watcher.on('addDir', (path, stats) => {
      this._triggerDebounced('addDir', path, stats);
    });

    // Directory deleted
    this.watcher.on('unlinkDir', (path) => {
      this._triggerDebounced('unlinkDir', path);
    });

    // Error occurred
    this.watcher.on('error', (error) => {
      this._triggerImmediate('error', error);
    });

    // Initial scan complete
    this.watcher.on('ready', () => {
      console.log('Initial scan complete. Ready for changes.');
      this._triggerImmediate('ready', null);
    });

    return this;
  }

  /**
   * Stop watching
   */
  async stop() {
    if (!this.watcher) {
      console.warn('Watcher not started');
      return;
    }

    // Clear all pending debounce timers
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();

    await this.watcher.close();
    this.watcher = null;
    console.log('File watcher stopped');
  }

  /**
   * Get watched paths
   */
  getWatched() {
    return this.watcher ? this.watcher.getWatched() : {};
  }
}

export default FileWatcher;
