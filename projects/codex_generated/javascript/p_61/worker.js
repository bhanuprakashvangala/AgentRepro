import 'dotenv/config';
import { jobQueue } from './queue.js';

jobQueue.process('email', async (job) => {
  job.progress(30);
  await new Promise((resolve) => setTimeout(resolve, 500));
  job.progress(80);
  await new Promise((resolve) => setTimeout(resolve, 500));
  console.log(`Sent email to ${job.data.to}`);
  return { delivered: Date.now() };
});

jobQueue.process('report', async (job) => {
  console.log(`Generating report ${job.data.reportId}`);
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return { path: `/reports/${job.data.reportId}.pdf` };
});

jobQueue.process('cleanup', async (job) => {
  if (job.attemptsMade < 1) {
    throw new Error('Simulated cleanup failure');
  }
  console.log(`Cleanup completed for items older than ${job.data.days} days`);
  return { removed: 42 };
});

jobQueue.on('progress', (job, progress) => {
  console.log(`Job ${job.id} progress: ${progress}%`);
});

jobQueue.on('completed', (job, result) => {
  console.log(`Job ${job.id} completed with result`, result);
});

jobQueue.on('failed', (job, err) => {
  console.error(`Job ${job.id} failed:`, err.message);
});

process.on('SIGINT', async () => {
  await jobQueue.close();
  process.exit(0);
});
