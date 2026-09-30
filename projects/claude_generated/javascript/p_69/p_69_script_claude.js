const redis = require('redis');

class CacheService {
  constructor(options = {}) {
    this.options = {
      host: options.host || '127.0.0.1',
      port: options.port || 6379,
      password: options.password,
      db: options.db || 0,
      keyPrefix: options.keyPrefix || 'cache:',
      defaultTTL: options.defaultTTL || 3600 // 1 hour
    };

    this.client = null;
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0
    };
  }

  /**
   * Connect to Redis
   */
  async connect() {
    try {
      this.client = redis.createClient({
        socket: {
          host: this.options.host,
          port: this.options.port
        },
        password: this.options.password,
        database: this.options.db
      });

      this.client.on('error', (err) => {
        console.error('Redis error:', err);
      });

      this.client.on('connect', () => {
        console.log('Connected to Redis');
      });

      await this.client.connect();
      return true;
    } catch (error) {
      console.error('Failed to connect to Redis:', error);
      throw error;
    }
  }

  /**
   * Get value from cache
   */
  async get(key) {
    try {
      const fullKey = this.options.keyPrefix + key;
      const value = await this.client.get(fullKey);

      if (value === null) {
        this.stats.misses++;
        return null;
      }

      this.stats.hits++;
      return JSON.parse(value);
    } catch (error) {
      console.error(`Error getting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Set value in cache
   */
  async set(key, value, ttl = this.options.defaultTTL) {
    try {
      const fullKey = this.options.keyPrefix + key;
      const serialized = JSON.stringify(value);

      if (ttl) {
        await this.client.setEx(fullKey, ttl, serialized);
      } else {
        await this.client.set(fullKey, serialized);
      }

      this.stats.sets++;
      return true;
    } catch (error) {
      console.error(`Error setting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Delete key from cache
   */
  async delete(key) {
    try {
      const fullKey = this.options.keyPrefix + key;
      const result = await this.client.del(fullKey);
      this.stats.deletes++;
      return result > 0;
    } catch (error) {
      console.error(`Error deleting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Check if key exists
   */
  async exists(key) {
    try {
      const fullKey = this.options.keyPrefix + key;
      const result = await this.client.exists(fullKey);
      return result === 1;
    } catch (error) {
      console.error(`Error checking existence of key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Increment numeric value
   */
  async increment(key, amount = 1) {
    try {
      const fullKey = this.options.keyPrefix + key;
      return await this.client.incrBy(fullKey, amount);
    } catch (error) {
      console.error(`Error incrementing key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Decrement numeric value
   */
  async decrement(key, amount = 1) {
    try {
      const fullKey = this.options.keyPrefix + key;
      return await this.client.decrBy(fullKey, amount);
    } catch (error) {
      console.error(`Error decrementing key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get multiple keys
   */
  async getMultiple(keys) {
    try {
      const fullKeys = keys.map(k => this.options.keyPrefix + k);
      const values = await this.client.mGet(fullKeys);

      return values.map((v, i) => {
        if (v === null) {
          this.stats.misses++;
          return null;
        }
        this.stats.hits++;
        return { key: keys[i], value: JSON.parse(v) };
      });
    } catch (error) {
      console.error('Error getting multiple keys:', error);
      throw error;
    }
  }

  /**
   * Set multiple keys
   */
  async setMultiple(entries, ttl = this.options.defaultTTL) {
    try {
      for (const [key, value] of Object.entries(entries)) {
        await this.set(key, value, ttl);
      }
      return true;
    } catch (error) {
      console.error('Error setting multiple keys:', error);
      throw error;
    }
  }

  /**
   * Flush all cache keys with prefix
   */
  async flush() {
    try {
      const pattern = this.options.keyPrefix + '*';
      const keys = [];

      for await (const key of this.client.scanIterator({ MATCH: pattern, COUNT: 100 })) {
        keys.push(key);
      }

      if (keys.length > 0) {
        await this.client.del(keys);
      }

      return keys.length;
    } catch (error) {
      console.error('Error flushing cache:', error);
      throw error;
    }
  }

  /**
   * Get all keys matching pattern
   */
  async getKeys(pattern = '*') {
    try {
      const fullPattern = this.options.keyPrefix + pattern;
      const keys = [];

      for await (const key of this.client.scanIterator({ MATCH: fullPattern, COUNT: 100 })) {
        keys.push(key.replace(this.options.keyPrefix, ''));
      }

      return keys;
    } catch (error) {
      console.error('Error getting keys:', error);
      throw error;
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      ...this.stats,
      hitRate: this.stats.hits + this.stats.misses > 0
        ? ((this.stats.hits / (this.stats.hits + this.stats.misses)) * 100).toFixed(2) + '%'
        : '0%'
    };
  }

  /**
   * Close Redis connection
   */
  async disconnect() {
    if (this.client) {
      await this.client.quit();
      console.log('Disconnected from Redis');
    }
  }
}

module.exports = CacheService;

// Example usage
if (require.main === module) {
  const cache = new CacheService();

  cache.connect().then(async () => {
    console.log('Cache service ready!');

    // Example operations
    await cache.set('user:123', { name: 'Alice', email: 'alice@example.com' });
    const user = await cache.get('user:123');
    console.log('User:', user);

    console.log('Stats:', cache.getStats());

    await cache.disconnect();
  }).catch(console.error);
}
