const Queue = require('bull');

const myQueue = new Queue('my-queue', 'redis://127.0.0.1:6379');

async function addJob() {
    const job = await myQueue.add({ data: 'my-job' }, {
        attempts: 3, // Retry 3 times if the job fails
        backoff: 5000 // 5 seconds delay between retries
    });
    console.log(`Added job ${job.id}`);
}

addJob();
