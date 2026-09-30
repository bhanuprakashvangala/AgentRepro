const Queue = require('bull');

// Create a new queue instance
const jobQueue = new Queue('task-queue', {
  redis: {
    host: '127.0.0.1',
    port: 6379,
  },
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: 100,
    removeOnFail: 50,
  },
});

// Job processor function
jobQueue.process('email', async (job) => {
  console.log(`\n[PROCESSING] Email job #${job.id}`);
  console.log('Data:', job.data);

  // Update progress
  await job.progress(20);

  // Simulate email processing
  await new Promise(resolve => setTimeout(resolve, 1000));
  await job.progress(50);

  // Simulate potential failure for testing retry logic
  if (job.data.shouldFail && job.attemptsMade < 2) {
    await job.progress(60);
    throw new Error('Simulated failure - will retry');
  }

  await job.progress(80);
  await new Promise(resolve => setTimeout(resolve, 500));
  await job.progress(100);

  return {
    success: true,
    recipient: job.data.recipient,
    sentAt: new Date().toISOString()
  };
});

jobQueue.process('data-processing', 3, async (job) => {
  console.log(`\n[PROCESSING] Data processing job #${job.id} (Concurrency: 3)`);
  console.log('Data:', job.data);

  await job.progress(25);

  // Simulate heavy data processing
  const items = job.data.items || [];
  for (let i = 0; i < items.length; i++) {
    await new Promise(resolve => setTimeout(resolve, 300));
    await job.progress(Math.round(((i + 1) / items.length) * 100));
  }

  return {
    success: true,
    processedCount: items.length,
    completedAt: new Date().toISOString()
  };
});

// Event listeners for monitoring
jobQueue.on('completed', (job, result) => {
  console.log(`\n✓ Job #${job.id} completed successfully!`);
  console.log('Result:', result);
});

jobQueue.on('failed', (job, err) => {
  console.log(`\n✗ Job #${job.id} failed after ${job.attemptsMade} attempts`);
  console.log('Error:', err.message);

  if (job.attemptsMade >= job.opts.attempts) {
    console.log('  → Max retries reached. Job moved to failed queue.');
  } else {
    console.log(`  → Will retry. Next attempt in ${job.opts.backoff.delay * Math.pow(2, job.attemptsMade - 1)}ms`);
  }
});

jobQueue.on('progress', (job, progress) => {
  console.log(`Job #${job.id} progress: ${progress}%`);
});

jobQueue.on('active', (job) => {
  console.log(`\n→ Job #${job.id} started processing`);
});

jobQueue.on('stalled', (job) => {
  console.log(`\n⚠ Job #${job.id} stalled and will be reprocessed`);
});

jobQueue.on('error', (error) => {
  console.error('Queue error:', error);
});

console.log('✓ Bull job queue initialized and ready!');
console.log('Redis connection: 127.0.0.1:6379');
console.log('Queue name: task-queue');
console.log('\nListening for jobs...\n');

module.exports = jobQueue;
