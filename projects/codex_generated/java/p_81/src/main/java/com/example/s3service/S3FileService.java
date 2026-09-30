package com.example.s3service;

import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.exception.SdkClientException;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3AsyncClient;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.NoSuchKeyException;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;
import software.amazon.awssdk.services.s3.presigner.model.PresignedGetObjectRequest;
import software.amazon.awssdk.transfer.s3.S3TransferManager;
import software.amazon.awssdk.transfer.s3.model.UploadFileRequest;
import software.amazon.awssdk.transfer.s3.progress.LoggingTransferListener;
import software.amazon.awssdk.transfer.s3.FileUpload;

/**
 * High-level wrapper around S3 operations for uploading, downloading, and generating presigned URLs.
 * The same instance can be reused for multiple operations; remember to close it when finished.
 */
public class S3FileService implements AutoCloseable {

    private static final Logger logger = LoggerFactory.getLogger(S3FileService.class);

    private final S3Client s3Client;
    private final S3AsyncClient s3AsyncClient;
    private final S3Presigner presigner;
    private final S3TransferManager transferManager;

    public S3FileService(Region region) {
        DefaultCredentialsProvider credentialsProvider = DefaultCredentialsProvider.create();
        this.s3Client = S3Client.builder()
                .region(region)
                .credentialsProvider(credentialsProvider)
                .build();
        this.s3AsyncClient = S3AsyncClient.builder()
                .region(region)
                .credentialsProvider(credentialsProvider)
                .build();
        this.transferManager = S3TransferManager.builder()
                .s3Client(s3AsyncClient)
                .build();
        this.presigner = S3Presigner.builder()
                .region(region)
                .credentialsProvider(credentialsProvider)
                .build();
    }

    /**
     * Uploads a file to S3 using a simple PUT request. For files larger than 100 MB,
     * prefer {@link #uploadLargeFile(String, String, Path)} which uses multipart uploads.
     */
    public void uploadFile(String bucket, String key, Path filePath) throws IOException {
        logger.info("Uploading {} to s3://{}/{}", filePath, bucket, key);
        if (!Files.exists(filePath)) {
            throw new IOException("File not found: " + filePath);
        }
        PutObjectRequest putRequest = PutObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build();
        s3Client.putObject(putRequest, RequestBody.fromFile(filePath));
        logger.info("Upload complete");
    }

    /**
     * Downloads an object from S3 and writes it to {@code destination}.
     */
    public void downloadFile(String bucket, String key, Path destination) throws IOException {
        logger.info("Downloading s3://{}/{} to {}", bucket, key, destination);
        if (destination.getParent() != null) {
            Files.createDirectories(destination.getParent());
        }
        GetObjectRequest getRequest = GetObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build();
        try {
            s3Client.getObject(getRequest, destination);
        } catch (NoSuchKeyException e) {
            throw new IOException("Object not found: s3://" + bucket + "/" + key, e);
        }
        logger.info("Download complete");
    }

    /**
     * Uploads a large file using multipart upload via the high-level transfer manager.
     */
    public void uploadLargeFile(String bucket, String key, Path filePath) throws IOException {
        logger.info("Multipart upload {} to s3://{}/{}", filePath, bucket, key);
        if (!Files.exists(filePath)) {
            throw new IOException("File not found: " + filePath);
        }
        UploadFileRequest uploadFileRequest = UploadFileRequest.builder()
                .putObjectRequest(b -> b.bucket(bucket).key(key))
                .source(filePath)
                .addTransferListener(LoggingTransferListener.create())
                .build();
        FileUpload upload = transferManager.uploadFile(uploadFileRequest);
        upload.completionFuture().join();
        logger.info("Multipart upload complete");
    }

    /**
     * Generates a presigned URL for downloading the specified object within the provided expiry duration.
     */
    public URL generatePresignedUrl(String bucket, String key, Duration expiry) {
        logger.info("Generating presigned URL for s3://{}/{} expires in {}", bucket, key, expiry);
        if (expiry.isNegative() || expiry.isZero()) {
            throw SdkClientException.create("Expiry must be positive");
        }
        PresignedGetObjectRequest presignedRequest = presigner.presignGetObject(
                GetObjectPresignRequest.builder()
                        .signatureDuration(expiry)
                        .getObjectRequest(b -> b.bucket(bucket).key(key))
                        .build()
        );
        return presignedRequest.url();
    }

    @Override
    public void close() {
        transferManager.close();
        s3AsyncClient.close();
        s3Client.close();
        presigner.close();
        logger.info("Resources closed");
    }
}
