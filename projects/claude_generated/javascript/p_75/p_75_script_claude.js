const Agenda = require('agenda');

class TaskScheduler {
  constructor(mongoConnectionString, dbName = 'scheduler') {
    this.connectionString = mongoConnectionString || 'mongodb://localhost:27017/scheduler';
    this.agenda = new Agenda({
      db: { address: this.connectionString, collection: 'jobs' },
      processEvery: '30 seconds',
      maxConcurrency: 20
    });

    this.setupEventHandlers();
  }

  /**
   * Setup event handlers
   */
  setupEventHandlers() {
    this.agenda.on('ready', () => {
      console.log('Agenda connected to MongoDB and ready');
    });

    this.agenda.on('error', (error) => {
      console.error('Agenda error:', error);
    });

    this.agenda.on('start', (job) => {
      console.log(`Job <${job.attrs.name}> starting`);
    });

    this.agenda.on('complete', (job) => {
      console.log(`Job <${job.attrs.name}> completed`);
    });

    this.agenda.on('fail', (error, job) => {
      console.error(`Job <${job.attrs.name}> failed:`, error);
    });
  }

  /**
   * Define a job
   */
  defineJob(jobName, handler) {
    this.agenda.define(jobName, async (job) => {
      console.log(`Executing job: ${jobName}`);
      console.log('Job data:', job.attrs.data);

      try {
        await handler(job.attrs.data);
      } catch (error) {
        console.error(`Error in job ${jobName}:`, error);
        throw error;
      }
    });
  }

  /**
   * Schedule a one-time job
   */
  async scheduleJob(jobName, when, data = {}) {
    await this.agenda.schedule(when, jobName, data);
    console.log(`Scheduled job "${jobName}" for ${when}`);
  }

  /**
   * Schedule a recurring job
   */
  async scheduleRecurring(jobName, interval, data = {}) {
    await this.agenda.every(interval, jobName, data);
    console.log(`Scheduled recurring job "${jobName}" every ${interval}`);
  }

  /**
   * Cancel a job
   */
  async cancelJob(query) {
    const numRemoved = await this.agenda.cancel(query);
    console.log(`Cancelled ${numRemoved} jobs`);
    return numRemoved;
  }

  /**
   * List all jobs
   */
  async listJobs() {
    const jobs = await this.agenda.jobs({});
    return jobs.map(job => ({
      name: job.attrs.name,
      nextRunAt: job.attrs.nextRunAt,
      lastRunAt: job.attrs.lastRunAt,
      lastFinishedAt: job.attrs.lastFinishedAt,
      failCount: job.attrs.failCount,
      data: job.attrs.data
    }));
  }

  /**
   * Start the scheduler
   */
  async start() {
    await this.agenda.start();
    console.log('Task scheduler started');
  }

  /**
   * Stop the scheduler
   */
  async stop() {
    await this.agenda.stop();
    console.log('Task scheduler stopped');
  }

  /**
   * Graceful shutdown
   */
  async gracefulShutdown() {
    console.log('Shutting down gracefully...');
    await this.agenda.stop();
    process.exit(0);
  }
}

module.exports = TaskScheduler;

// Example usage
if (require.main === module) {
  const scheduler = new TaskScheduler();

  // Define jobs
  scheduler.defineJob('sendEmail', async (data) => {
    console.log(`Sending email to ${data.to}: ${data.subject}`);
    // Email sending logic here
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Email sent!');
  });

  scheduler.defineJob('cleanupDatabase', async () => {
    console.log('Running database cleanup...');
    // Cleanup logic here
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('Cleanup completed!');
  });

  scheduler.defineJob('generateReport', async (data) => {
    console.log(`Generating ${data.reportType} report...`);
    // Report generation logic
    await new Promise(resolve => setTimeout(resolve, 1500));
    console.log('Report generated!');
  });

  scheduler.defineJob('backupData', async () => {
    console.log('Starting data backup...');
    // Backup logic here
    await new Promise(resolve => setTimeout(resolve, 3000));
    console.log('Backup completed!');
  });

  // Start scheduler
  scheduler.start().then(async () => {
    // Schedule example jobs

    // One-time job in 5 seconds
    await scheduler.scheduleJob('sendEmail', '5 seconds', {
      to: 'user@example.com',
      subject: 'Welcome!',
      body: 'Thank you for signing up'
    });

    // Recurring job every 2 minutes
    await scheduler.scheduleRecurring('cleanupDatabase', '2 minutes');

    // Daily report at 9 AM
    await scheduler.scheduleRecurring('generateReport', '0 9 * * *', {
      reportType: 'daily'
    });

    // Weekly backup on Sundays at midnight
    await scheduler.scheduleRecurring('backupData', '0 0 * * 0');

    console.log('\nScheduled jobs:');
    const jobs = await scheduler.listJobs();
    jobs.forEach(job => {
      console.log(`  - ${job.name}: Next run at ${job.nextRunAt}`);
    });
  });

  // Handle graceful shutdown
  process.on('SIGINT', () => scheduler.gracefulShutdown());
  process.on('SIGTERM', () => scheduler.gracefulShutdown());
}
