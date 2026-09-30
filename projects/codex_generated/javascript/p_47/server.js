import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import nodemailer from 'nodemailer';
import handlebars from 'handlebars';
import cron from 'node-cron';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const schedulePath = path.join(__dirname, 'schedule.json');
const templatesDir = path.join(__dirname, 'templates');
const attachmentsDir = path.join(__dirname, 'attachments');

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT || 587),
  secure: process.env.SMTP_SECURE === 'true',
  auth: process.env.SMTP_USER && process.env.SMTP_PASS ? {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  } : undefined
});

async function verifyTransporter() {
  try {
    await transporter.verify();
    console.log('SMTP transporter verified. Ready to send emails.');
  } catch (error) {
    console.error('Failed to verify transporter:', error.message);
  }
}

function loadTemplate(templateName) {
  const templatePath = path.join(templatesDir, templateName);
  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template not found: ${templateName}`);
  }
  const templateContent = fs.readFileSync(templatePath, 'utf-8');
  return handlebars.compile(templateContent);
}

async function sendEmail({ to, subject, template, context = {}, attachments = [] }) {
  const compileTemplate = loadTemplate(template);
  const html = compileTemplate(context);

  const formattedAttachments = attachments.map((file) => {
    const filePath = path.isAbsolute(file) ? file : path.join(__dirname, file);
    if (!fs.existsSync(filePath)) {
      throw new Error(`Attachment not found: ${filePath}`);
    }
    return {
      filename: path.basename(filePath),
      path: filePath
    };
  });

  const info = await transporter.sendMail({
    from: process.env.MAIL_FROM || process.env.SMTP_USER,
    to,
    subject,
    html,
    attachments: formattedAttachments
  });
  console.log(`Email sent to ${to}: ${info.messageId}`);
}

function loadScheduleConfig() {
  if (!fs.existsSync(schedulePath)) {
    console.warn('schedule.json not found. No jobs scheduled.');
    return { jobs: [] };
  }
  try {
    const raw = fs.readFileSync(schedulePath, 'utf-8');
    return JSON.parse(raw);
  } catch (error) {
    console.error('Failed to parse schedule.json:', error.message);
    return { jobs: [] };
  }
}

function scheduleJobs() {
  const config = loadScheduleConfig();
  if (!Array.isArray(config.jobs)) {
    console.error('schedule.json jobs should be an array.');
    return;
  }

  config.jobs.forEach((job) => {
    if (!job.cron || !job.to || !job.subject || !job.template) {
      console.error('Invalid job configuration:', job);
      return;
    }

    cron.schedule(job.cron, async () => {
      try {
        await sendEmail({
          to: Array.isArray(job.to) ? job.to.join(',') : job.to,
          subject: job.subject,
          template: job.template,
          context: job.context || {},
          attachments: job.attachments || []
        });
      } catch (error) {
        console.error('Failed to send scheduled email:', error.message);
      }
    });

    console.log(`Scheduled job for ${job.subject} with cron ${job.cron}`);
  });
}

async function main() {
  console.log('Starting email automation service...');
  await verifyTransporter();
  scheduleJobs();
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
