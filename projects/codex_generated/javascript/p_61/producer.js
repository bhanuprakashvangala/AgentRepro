import 'dotenv/config';
import { jobQueue } from './queue.js';

const jobs = [
  { name: 'email', data: { to: 'alice@example.com', subject: 'Welcome' } },
  { name: 'report', data: { reportId: 'rpt-123' } },
  { name: 'cleanup', data: { days: 30 } }
];

async function enqueueJobs() {
  for (const job of jobs) {
    const queued = await jobQueue.add(job.name, job.data, {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 1000
      }
    });
    console.log(`Enqueued job ${queued.id} of type ${job.name}`);
  }
  await jobQueue.close();
}

enqueueJobs().catch((error) => {
  console.error('Failed to enqueue jobs:', error);
  process.exit(1);
});
