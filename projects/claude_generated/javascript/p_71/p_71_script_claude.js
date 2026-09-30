const { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand, ListObjectsV2Command, CopyObjectCommand, HeadObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');
const fs = require('fs');
require('dotenv').config();

class S3Service {
  constructor(bucketName, region = 'us-east-1') {
    this.bucketName = bucketName;
    this.region = region;

    this.s3Client = new S3Client({
      region: this.region,
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
      }
    });

    console.log(`S3Service initialized for bucket: ${bucketName}`);
  }

  /**
   * Upload file to S3
   */
  async uploadFile(key, fileContent, contentType = 'application/octet-stream') {
    try {
      const command = new PutObjectCommand({
        Bucket: this.bucketName,
        Key: key,
        Body: fileContent,
        ContentType: contentType
      });

      const response = await this.s3Client.send(command);
      console.log(`File uploaded: ${key}`);
      return {
        success: true,
        key: key,
        etag: response.ETag,
        url: `https://${this.bucketName}.s3.${this.region}.amazonaws.com/${key}`
      };
    } catch (error) {
      console.error('Upload error:', error);
      throw new Error(`Failed to upload file: ${error.message}`);
    }
  }

  /**
   * Download file from S3
   */
  async downloadFile(key) {
    try {
      const command = new GetObjectCommand({
        Bucket: this.bucketName,
        Key: key
      });

      const response = await this.s3Client.send(command);
      const stream = response.Body;

      // Convert stream to buffer
      const chunks = [];
      for await (const chunk of stream) {
        chunks.push(chunk);
      }

      return Buffer.concat(chunks);
    } catch (error) {
      console.error('Download error:', error);
      throw new Error(`Failed to download file: ${error.message}`);
    }
  }

  /**
   * Delete file from S3
   */
  async deleteFile(key) {
    try {
      const command = new DeleteObjectCommand({
        Bucket: this.bucketName,
        Key: key
      });

      await this.s3Client.send(command);
      console.log(`File deleted: ${key}`);
      return { success: true, key: key };
    } catch (error) {
      console.error('Delete error:', error);
      throw new Error(`Failed to delete file: ${error.message}`);
    }
  }

  /**
   * List files in bucket
   */
  async listFiles(prefix = '', maxKeys = 1000) {
    try {
      const command = new ListObjectsV2Command({
        Bucket: this.bucketName,
        Prefix: prefix,
        MaxKeys: maxKeys
      });

      const response = await this.s3Client.send(command);
      return response.Contents || [];
    } catch (error) {
      console.error('List error:', error);
      throw new Error(`Failed to list files: ${error.message}`);
    }
  }

  /**
   * Get presigned URL for upload
   */
  async getPresignedUploadUrl(key, expiresIn = 3600) {
    try {
      const command = new PutObjectCommand({
        Bucket: this.bucketName,
        Key: key
      });

      const url = await getSignedUrl(this.s3Client, command, { expiresIn });
      return url;
    } catch (error) {
      console.error('Presigned upload URL error:', error);
      throw new Error(`Failed to generate presigned upload URL: ${error.message}`);
    }
  }

  /**
   * Get presigned URL for download
   */
  async getPresignedDownloadUrl(key, expiresIn = 3600) {
    try {
      const command = new GetObjectCommand({
        Bucket: this.bucketName,
        Key: key
      });

      const url = await getSignedUrl(this.s3Client, command, { expiresIn });
      return url;
    } catch (error) {
      console.error('Presigned download URL error:', error);
      throw new Error(`Failed to generate presigned download URL: ${error.message}`);
    }
  }

  /**
   * Copy file within S3
   */
  async copyFile(sourceKey, destinationKey) {
    try {
      const command = new CopyObjectCommand({
        Bucket: this.bucketName,
        CopySource: `${this.bucketName}/${sourceKey}`,
        Key: destinationKey
      });

      await this.s3Client.send(command);
      console.log(`File copied: ${sourceKey} -> ${destinationKey}`);
      return { success: true, source: sourceKey, destination: destinationKey };
    } catch (error) {
      console.error('Copy error:', error);
      throw new Error(`Failed to copy file: ${error.message}`);
    }
  }

  /**
   * Check if file exists
   */
  async fileExists(key) {
    try {
      const command = new HeadObjectCommand({
        Bucket: this.bucketName,
        Key: key
      });

      await this.s3Client.send(command);
      return true;
    } catch (error) {
      if (error.name === 'NotFound') {
        return false;
      }
      throw error;
    }
  }
}

module.exports = S3Service;

// Example usage
if (require.main === module) {
  const s3 = new S3Service(process.env.S3_BUCKET_NAME);

  // Example: Upload a file
  const testContent = Buffer.from('Hello, S3!');
  s3.uploadFile('test/hello.txt', testContent, 'text/plain')
    .then(result => console.log('Upload result:', result))
    .catch(console.error);
}
