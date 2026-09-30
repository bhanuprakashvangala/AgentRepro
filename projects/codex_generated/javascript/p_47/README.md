# Email Automation Service

Node.js automation script that sends scheduled HTML emails using Nodemailer, Handlebars templates, attachments, and node-cron scheduling.

## Setup
```bash
npm install
```

Create a `.env` file (or export env vars):
```
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your_username
SMTP_PASS=your_password
MAIL_FROM="Your Name <no-reply@example.com>"
```

Configure jobs in `schedule.json`. Example job (runs every 30 seconds):
```json
{
  "cron": "*/30 * * * * *",
  "to": ["recipient@example.com"],
  "subject": "Welcome",
  "template": "welcome.html",
  "context": { "name": "Friend", "company": "Acme" },
  "attachments": ["attachments/sample.txt"]
}
```

## Run
```bash
npm start
```
The service verifies SMTP credentials, loads jobs, and schedules them via cron expressions.

## Files
- `server.js` – main script handling transport setup, rendering, and scheduling.
- `templates/` – Handlebars HTML email templates with `{{placeholders}}`.
- `attachments/` – Files referenced in job configurations.
- `schedule.json` – List of jobs to run.

Modify templates and job contexts as needed for your automation workflow.
