import 'dotenv/config';
import Redis from 'ioredis';

const nodes = process.env.REDIS_CLUSTER_NODES
  ? process.env.REDIS_CLUSTER_NODES.split(',').map((node) => {
      const [host, port] = node.split(':');
      return { host, port: Number(port) };
    })
  : [
      { host: '127.0.0.1', port: 7000 },
      { host: '127.0.0.1', port: 7001 },
      { host: '127.0.0.1', port: 7002 }
    ];

export const redis = new Redis.Cluster(nodes, {
  redisOptions: {
    maxRetriesPerRequest: 3,
    connectTimeout: 5000
  }
});

redis.on('error', (error) => console.error('Redis error:', error.message));
redis.on('connect', () => console.log('Connected to Redis cluster'));
redis.on('end', () => console.warn('Redis cluster connection closed'));
redis.on('reconnecting', (delay) => console.log(`Reconnecting to cluster in ${delay}ms`));

export async function setCache(key, value, ttlSeconds = 300) {
  const payload = typeof value === 'string' ? value : JSON.stringify(value);
  await redis.set(key, payload, 'EX', ttlSeconds);
}

export async function getCache(key) {
  const data = await redis.get(key);
  if (!data) return null;
  try {
    return JSON.parse(data);
  } catch (error) {
    return data;
  }
}
