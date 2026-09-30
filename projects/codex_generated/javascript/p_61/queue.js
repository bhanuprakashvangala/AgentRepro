import 'dotenv/config';
import Queue from 'bull';

const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';

export const jobQueue = new Queue('jobs', REDIS_URL);
