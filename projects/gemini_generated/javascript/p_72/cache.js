const Redis = require('ioredis');

// Redis cluster configuration
const clusterNodes = [
    { host: '127.0.0.1', port: 7000 },
    { host: '127.0.0.1', port: 7001 },
    { host: '127.0.0.1', port: 7002 }
];

const redis = new Redis.Cluster(clusterNodes);

redis.on('connect', () => {
    console.log('Connected to Redis Cluster');
});

redis.on('error', (err) => {
    console.error('Redis Cluster Error:', err);
});

async function runCacheOperations() {
    try {
        // Set a value with TTL (Time To Live) of 10 seconds
        await redis.set('mykey', 'myvalue', 'EX', 10);
        console.log('Set mykey: myvalue (expires in 10s)');

        // Get the value
        let value = await redis.get('mykey');
        console.log('Get mykey:', value);

        // Wait for 5 seconds
        await new Promise(resolve => setTimeout(resolve, 5000));
        value = await redis.get('mykey');
        console.log('Get mykey after 5s:', value);

        // Wait for another 6 seconds (total 11s, key should be expired)
        await new Promise(resolve => setTimeout(resolve, 6000));
        value = await redis.get('mykey');
        console.log('Get mykey after 11s:', value);

    } catch (error) {
        console.error('Error during cache operations:', error);
    } finally {
        redis.disconnect();
    }
}

runCacheOperations();
