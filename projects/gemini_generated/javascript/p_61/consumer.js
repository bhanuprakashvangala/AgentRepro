const Queue = require('bull');

const myQueue = new Queue('my-queue', 'redis://127.0.0.1:6379');

myQueue.process(async (job) => {
    console.log(`Processing job ${job.id} with data:`, job.data);

    // Simulate a task that might fail
    if (Math.random() < 0.5) {
        throw new Error('Job failed');
    }

    return Promise.resolve();
});

myQueue.on('completed', (job, result) => {
    console.log(`Job ${job.id} completed with result:`, result);
});

myQueue.on('failed', (job, err) => {
    console.log(`Job ${job.id} failed with error:`, err.message);
});

console.log('Worker is running...');
