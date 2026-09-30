# Email Automation Service

This project is an email automation service with templates, built with Nodemailer and node-cron.

## Requirements

- Node.js
- npm
- An email account (e.g., from Ethereal for testing)

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your email credentials. You can generate test credentials from [Ethereal](https://ethereal.email/).

    ```
    EMAIL_HOST=smtp.ethereal.email
    EMAIL_PORT=587
    EMAIL_USER=YOUR_ETHEREAL_USER
    EMAIL_PASS=YOUR_ETHEREAL_PASSWORD
    ```

## Usage

1.  Start the service:

    ```bash
    npm start
    ```

2.  The service will send an email every minute to a test recipient. You can check the console for the preview URL from Ethereal.
