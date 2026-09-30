require('dotenv').config();
const nodemailer = require('nodemailer');
const cron = require('node-cron');
const fs = require('fs');

// Create a transporter object using the default SMTP transport
const transporter = nodemailer.createTransport({
    host: process.env.EMAIL_HOST,
    port: process.env.EMAIL_PORT,
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

// Function to send an email
const sendEmail = async (to, subject, templatePath, templateData, attachments) => {
    try {
        let html = fs.readFileSync(templatePath, 'utf8');
        for (const key in templateData) {
            html = html.replace(new RegExp(`{{${key}}}`, 'g'), templateData[key]);
        }

        const mailOptions = {
            from: '"Your Name" <your-email@example.com>',
            to: to,
            subject: subject,
            html: html,
            attachments: attachments
        };

        const info = await transporter.sendMail(mailOptions);
        console.log('Message sent: %s', info.messageId);
        console.log('Preview URL: %s', nodemailer.getTestMessageUrl(info));
    } catch (error) {
        console.error('Error sending email:', error);
    }
};

// Schedule a task to run every minute
cron.schedule('* * * * *', () => {
    console.log('Running a task every minute');

    const to = 'test-recipient@example.com';
    const subject = 'Scheduled Email';
    const templatePath = './email_template.html';
    const templateData = { name: 'John Doe' };
    const attachments = [
        {
            filename: 'test.txt',
            content: 'This is a test attachment.'
        }
    ];

    sendEmail(to, subject, templatePath, templateData, attachments);
});

console.log('Email automation service started. Scheduled to run every minute.');
