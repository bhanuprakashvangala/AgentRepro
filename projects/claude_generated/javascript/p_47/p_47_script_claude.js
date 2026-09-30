import nodemailer from 'nodemailer';
import cron from 'node-cron';
import fs from 'fs';
import path from 'path';

/**
 * Email Automation Service
 * Handles email sending with templates, attachments, and scheduling
 */
class EmailService {
  constructor(config) {
    this.transporter = nodemailer.createTransport({
      host: config.host || 'smtp.gmail.com',
      port: config.port || 587,
      secure: config.secure || false,
      auth: {
        user: config.user,
        pass: config.pass
      }
    });

    this.scheduledJobs = new Map();
  }

  async verifyConnection() {
    try {
      await this.transporter.verify();
      console.log('✓ SMTP connection verified');
      return true;
    } catch (error) {
      console.error('✗ SMTP connection failed:', error.message);
      return false;
    }
  }

  async sendEmail(options) {
    try {
      const mailOptions = {
        from: options.from,
        to: options.to,
        subject: options.subject,
        html: options.html || this.renderTemplate(options.template, options.data),
        attachments: options.attachments || []
      };

      if (options.cc) mailOptions.cc = options.cc;
      if (options.bcc) mailOptions.bcc = options.bcc;

      const info = await this.transporter.sendMail(mailOptions);
      console.log('✓ Email sent:', info.messageId);
      return { success: true, messageId: info.messageId };
    } catch (error) {
      console.error('✗ Email send failed:', error.message);
      return { success: false, error: error.message };
    }
  }

  renderTemplate(templateName, data = {}) {
    const templates = {
      welcome: (data) => `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9f9f9; }
            .button { display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
            .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>Welcome to ${data.appName || 'Our Service'}!</h1>
            </div>
            <div class="content">
              <h2>Hello ${data.name || 'User'}!</h2>
              <p>Thank you for joining us. We're excited to have you on board.</p>
              <p>${data.message || 'Get started by exploring our features.'}</p>
              ${data.actionUrl ? `<a href="${data.actionUrl}" class="button">Get Started</a>` : ''}
            </div>
            <div class="footer">
              <p>&copy; ${new Date().getFullYear()} ${data.appName || 'Our Company'}. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,

      notification: (data) => `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #2196F3; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #fff; border: 1px solid #ddd; }
            .alert { padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; margin: 10px 0; }
            .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>Notification</h1>
            </div>
            <div class="content">
              <h2>${data.title || 'Update'}</h2>
              <div class="alert">
                <strong>Notice:</strong> ${data.message || 'You have a new notification.'}
              </div>
              ${data.details ? `<p>${data.details}</p>` : ''}
            </div>
            <div class="footer">
              <p>This is an automated notification. Please do not reply to this email.</p>
            </div>
          </div>
        </body>
        </html>
      `,

      report: (data) => `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #673AB7; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #fff; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat { text-align: center; padding: 15px; background: #f5f5f5; border-radius: 5px; }
            .stat-value { font-size: 24px; font-weight: bold; color: #673AB7; }
            .stat-label { font-size: 14px; color: #777; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f5f5f5; font-weight: bold; }
            .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>${data.reportName || 'Report'}</h1>
              <p>${data.period || new Date().toLocaleDateString()}</p>
            </div>
            <div class="content">
              <h2>Summary</h2>
              <div class="stats">
                ${data.stats ? data.stats.map(stat => `
                  <div class="stat">
                    <div class="stat-value">${stat.value}</div>
                    <div class="stat-label">${stat.label}</div>
                  </div>
                `).join('') : ''}
              </div>
              ${data.notes ? `<p><strong>Notes:</strong> ${data.notes}</p>` : ''}
            </div>
            <div class="footer">
              <p>Generated on ${new Date().toLocaleString()}</p>
            </div>
          </div>
        </body>
        </html>
      `,

      invoice: (data) => `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { display: flex; justify-content: space-between; padding: 20px; border-bottom: 2px solid #333; }
            .content { padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f5f5f5; font-weight: bold; }
            .total { text-align: right; font-size: 18px; font-weight: bold; margin: 20px 0; }
            .footer { text-align: center; padding: 20px; color: #777; font-size: 12px; border-top: 1px solid #ddd; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <div>
                <h1>${data.companyName || 'Company Name'}</h1>
                <p>${data.companyAddress || ''}</p>
              </div>
              <div style="text-align: right;">
                <h2>INVOICE</h2>
                <p><strong>#${data.invoiceNumber || '0001'}</strong></p>
                <p>${data.date || new Date().toLocaleDateString()}</p>
              </div>
            </div>
            <div class="content">
              <h3>Bill To:</h3>
              <p>
                <strong>${data.customerName || 'Customer'}</strong><br>
                ${data.customerEmail || ''}<br>
                ${data.customerAddress || ''}
              </p>
              <table>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  ${data.items ? data.items.map(item => `
                    <tr>
                      <td>${item.description}</td>
                      <td>${item.quantity}</td>
                      <td>$${item.price.toFixed(2)}</td>
                      <td>$${(item.quantity * item.price).toFixed(2)}</td>
                    </tr>
                  `).join('') : ''}
                </tbody>
              </table>
              <div class="total">
                Total: $${data.total ? data.total.toFixed(2) : '0.00'}
              </div>
              ${data.notes ? `<p><strong>Notes:</strong> ${data.notes}</p>` : ''}
            </div>
            <div class="footer">
              <p>Thank you for your business!</p>
            </div>
          </div>
        </body>
        </html>
      `
    };

    if (!templates[templateName]) {
      throw new Error(`Template "${templateName}" not found`);
    }

    return templates[templateName](data);
  }

  scheduleEmail(cronExpression, emailOptions, jobName = null) {
    const name = jobName || `job-${Date.now()}`;

    if (this.scheduledJobs.has(name)) {
      console.warn(`Job "${name}" already exists. Stopping old job.`);
      this.stopScheduledEmail(name);
    }

    const job = cron.schedule(cronExpression, async () => {
      console.log(`Executing scheduled job: ${name}`);
      await this.sendEmail(emailOptions);
    });

    this.scheduledJobs.set(name, job);
    console.log(`✓ Email scheduled: ${name} (${cronExpression})`);

    return name;
  }

  stopScheduledEmail(jobName) {
    const job = this.scheduledJobs.get(jobName);
    if (job) {
      job.stop();
      this.scheduledJobs.delete(jobName);
      console.log(`✓ Scheduled job stopped: ${jobName}`);
      return true;
    }
    console.warn(`Job "${jobName}" not found`);
    return false;
  }

  listScheduledJobs() {
    return Array.from(this.scheduledJobs.keys());
  }

  createAttachment(filePath, filename = null) {
    return {
      filename: filename || path.basename(filePath),
      path: filePath
    };
  }

  createBufferAttachment(buffer, filename, contentType = 'application/octet-stream') {
    return {
      filename: filename,
      content: buffer,
      contentType: contentType
    };
  }
}

export default EmailService;
