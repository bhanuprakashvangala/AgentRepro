# File Upload Service with AWS S3

This project is a file upload service with AWS S3 integration, built with Express, Multer, and the AWS SDK.

## Requirements

- Node.js
- npm
- AWS Account with S3 bucket

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your AWS credentials and S3 bucket name:

    ```
    AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
    AWS_S3_BUCKET_NAME=YOUR_S3_BUCKET_NAME
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Open your browser and go to `http://localhost:3000`.

3.  Select a file and click "Upload".

4.  To download a file, enter the file key (from the upload response) and click "Get Download Link".
