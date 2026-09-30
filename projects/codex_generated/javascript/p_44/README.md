# S3 File Upload Service

Express server using Multer for multipart uploads and AWS SDK v3 for S3 integration. Upload files to an S3 bucket and generate presigned download URLs.

## Setup
```bash
npm install
```

Set environment variables:
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export S3_BUCKET=your_bucket
export PORT=5000 # optional
```

Start the server:
```bash
npm start
```

## API
- `POST /upload` – multipart form with `file` field. Returns `{ key }`.
- `GET /download/:key` – returns `{ url }` presigned for 15 minutes.

Use any HTTP client (curl, Postman) to send files. Files are uploaded via memory storage to avoid temp files.
