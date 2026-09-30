const express = require('express');
const multer = require('multer');
const { S3Client, PutObjectCommand, GetObjectCommand, HeadObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');
const path = require('path');
const crypto = require('crypto');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 5000;
const bucketName = process.env.S3_BUCKET;
const region = process.env.AWS_REGION || 'us-east-1';

if (!bucketName) {
  console.error('Missing S3_BUCKET environment variable.');
  process.exit(1);
}

const s3 = new S3Client({ region });
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 25 * 1024 * 1024 } });

app.use(express.json());

app.post('/upload', upload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' });
    }
    const extension = path.extname(req.file.originalname);
    const key = `${crypto.randomUUID()}${extension}`;

    const putCommand = new PutObjectCommand({
      Bucket: bucketName,
      Key: key,
      Body: req.file.buffer,
      ContentType: req.file.mimetype
    });

    await s3.send(putCommand);
    res.status(201).json({
      message: 'File uploaded successfully',
      key
    });
  } catch (error) {
    next(error);
  }
});

app.get('/download/:key', async (req, res, next) => {
  try {
    const { key } = req.params;
    const headCommand = new HeadObjectCommand({ Bucket: bucketName, Key: key });
    await s3.send(headCommand);

    const url = await getSignedUrl(
      s3,
      new GetObjectCommand({ Bucket: bucketName, Key: key }),
      { expiresIn: 60 * 15 }
    );

    res.json({ url });
  } catch (error) {
    if (error.$metadata && error.$metadata.httpStatusCode === 404) {
      return res.status(404).json({ message: 'File not found' });
    }
    next(error);
  }
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Internal Server Error' });
});

app.listen(port, () => {
  console.log(`File upload service listening on port ${port}`);
});
