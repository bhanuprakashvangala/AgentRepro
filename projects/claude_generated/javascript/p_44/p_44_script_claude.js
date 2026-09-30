import express from 'express';
import multer from 'multer';
import { S3Client, PutObjectCommand, GetObjectCommand, ListObjectsV2Command, DeleteObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import dotenv from 'dotenv';
import cors from 'cors';
import crypto from 'crypto';
import path from 'path';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configure AWS S3 Client
const s3Client = new S3Client({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});

const BUCKET_NAME = process.env.AWS_S3_BUCKET_NAME;
const PRESIGNED_URL_EXPIRATION = parseInt(process.env.PRESIGNED_URL_EXPIRATION) || 3600;

// Configure Multer for memory storage
const storage = multer.memoryStorage();

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    cb(null, true);
  },
});

// Helper function to generate unique filename
function generateUniqueFilename(originalFilename) {
  const timestamp = Date.now();
  const randomString = crypto.randomBytes(8).toString('hex');
  const extension = path.extname(originalFilename);
  const basename = path.basename(originalFilename, extension);
  return `${basename}-${timestamp}-${randomString}${extension}`;
}

// Helper function to upload file to S3
async function uploadToS3(file, key) {
  const params = {
    Bucket: BUCKET_NAME,
    Key: key,
    Body: file.buffer,
    ContentType: file.mimetype,
    Metadata: {
      originalName: file.originalname,
      uploadDate: new Date().toISOString(),
    },
  };

  const command = new PutObjectCommand(params);
  await s3Client.send(command);

  return {
    key: key,
    bucket: BUCKET_NAME,
    originalName: file.originalname,
    size: file.size,
    mimetype: file.mimetype,
  };
}

// Helper function to generate presigned URL
async function generatePresignedUrl(key, expiresIn = PRESIGNED_URL_EXPIRATION) {
  const command = new GetObjectCommand({
    Bucket: BUCKET_NAME,
    Key: key,
  });

  const url = await getSignedUrl(s3Client, command, { expiresIn });
  return url;
}

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'S3 File Upload Service is running' });
});

// Upload single file
app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const uniqueFilename = generateUniqueFilename(req.file.originalname);
    const fileKey = `uploads/${uniqueFilename}`;

    const uploadResult = await uploadToS3(req.file, fileKey);
    const presignedUrl = await generatePresignedUrl(fileKey);

    res.json({
      success: true,
      message: 'File uploaded successfully',
      file: uploadResult,
      downloadUrl: presignedUrl,
      expiresIn: PRESIGNED_URL_EXPIRATION,
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Failed to upload file', details: error.message });
  }
});

// Upload multiple files
app.post('/upload/multiple', upload.array('files', 10), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const uploadPromises = req.files.map(async (file) => {
      const uniqueFilename = generateUniqueFilename(file.originalname);
      const fileKey = `uploads/${uniqueFilename}`;
      const uploadResult = await uploadToS3(file, fileKey);
      const presignedUrl = await generatePresignedUrl(fileKey);

      return {
        ...uploadResult,
        downloadUrl: presignedUrl,
      };
    });

    const results = await Promise.all(uploadPromises);

    res.json({
      success: true,
      message: `${results.length} files uploaded successfully`,
      files: results,
      expiresIn: PRESIGNED_URL_EXPIRATION,
    });
  } catch (error) {
    console.error('Multiple upload error:', error);
    res.status(500).json({ error: 'Failed to upload files', details: error.message });
  }
});

// Generate presigned URL for existing file
app.post('/presigned-url', async (req, res) => {
  try {
    const { key, expiresIn } = req.body;

    if (!key) {
      return res.status(400).json({ error: 'File key is required' });
    }

    const expiration = expiresIn || PRESIGNED_URL_EXPIRATION;
    const presignedUrl = await generatePresignedUrl(key, expiration);

    res.json({
      success: true,
      key: key,
      downloadUrl: presignedUrl,
      expiresIn: expiration,
    });
  } catch (error) {
    console.error('Presigned URL error:', error);
    res.status(500).json({ error: 'Failed to generate presigned URL', details: error.message });
  }
});

// List files in bucket
app.get('/files', async (req, res) => {
  try {
    const prefix = req.query.prefix || 'uploads/';
    const maxKeys = parseInt(req.query.maxKeys) || 100;

    const command = new ListObjectsV2Command({
      Bucket: BUCKET_NAME,
      Prefix: prefix,
      MaxKeys: maxKeys,
    });

    const response = await s3Client.send(command);

    const files = (response.Contents || []).map(item => ({
      key: item.Key,
      size: item.Size,
      lastModified: item.LastModified,
    }));

    res.json({
      success: true,
      count: files.length,
      files: files,
    });
  } catch (error) {
    console.error('List files error:', error);
    res.status(500).json({ error: 'Failed to list files', details: error.message });
  }
});

// Delete file
app.delete('/files/:key(*)', async (req, res) => {
  try {
    const key = req.params.key;

    if (!key) {
      return res.status(400).json({ error: 'File key is required' });
    }

    const command = new DeleteObjectCommand({
      Bucket: BUCKET_NAME,
      Key: key,
    });

    await s3Client.send(command);

    res.json({
      success: true,
      message: 'File deleted successfully',
      key: key,
    });
  } catch (error) {
    console.error('Delete error:', error);
    res.status(500).json({ error: 'Failed to delete file', details: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File size exceeds limit (50MB)' });
    }
    if (error.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({ error: 'Too many files uploaded' });
    }
    return res.status(400).json({ error: error.message });
  }

  res.status(500).json({ error: 'Internal server error', details: error.message });
});

// Start server
app.listen(PORT, () => {
  console.log(`S3 File Upload Service running on port ${PORT}`);
  console.log(`Bucket: ${BUCKET_NAME}`);
  console.log(`Region: ${process.env.AWS_REGION}`);
});
