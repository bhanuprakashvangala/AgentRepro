package com.example.demo;

import com.amazonaws.AmazonServiceException;
import com.amazonaws.HttpMethod;
import com.amazonaws.SdkClientException;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.*;
import com.amazonaws.util.IOUtils;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class S3FileService {

    private static final String BUCKET_NAME = "your-unique-s3-bucket-name"; // Replace with your S3 bucket name
    private static final Regions CLIENT_REGION = Regions.US_EAST_1; // Replace with your desired AWS region

    public static void main(String[] args) throws IOException {
        AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                .withCredentials(new ProfileCredentialsProvider())
                .withRegion(CLIENT_REGION)
                .build();

        // Create a dummy file for upload
        File fileToUpload = new File("sample.txt");
        if (!fileToUpload.exists()) {
            fileToUpload.createNewFile();
            java.nio.file.Files.write(fileToUpload.toPath(), "Hello S3!".getBytes());
        }

        try {
            // Upload a file
            uploadFile(s3Client, BUCKET_NAME, "sample.txt", fileToUpload);

            // Download a file
            downloadFile(s3Client, BUCKET_NAME, "sample.txt");

            // Generate a pre-signed URL
            String presignedUrl = generatePresignedUrl(s3Client, BUCKET_NAME, "sample.txt");
            System.out.println("Pre-signed URL to download sample.txt: " + presignedUrl);

            // Multipart upload (for large files)
            File largeFile = new File("large_sample.txt");
            if (!largeFile.exists()) {
                largeFile.createNewFile();
                byte[] largeContent = new byte[10 * 1024 * 1024]; // 10 MB
                java.util.Arrays.fill(largeContent, (byte) 'A');
                java.nio.file.Files.write(largeFile.toPath(), largeContent);
            }
            multipartUpload(s3Client, BUCKET_NAME, "large_sample.txt", largeFile);

        } catch (AmazonServiceException e) {
            // The call was transmitted successfully, but Amazon S3 couldn't process 
            // it, so it returned an error response.
            e.printStackTrace();
        } catch (SdkClientException e) {
            // Amazon S3 couldn't be contacted for a response, or the client
            // couldn't parse the response from Amazon S3.
            e.printStackTrace();
        }
    }

    private static void uploadFile(AmazonS3 s3Client, String bucketName, String key, File file) {
        System.out.println("Uploading " + key + " to S3 bucket " + bucketName);
        s3Client.putObject(new PutObjectRequest(bucketName, key, file));
        System.out.println("Upload complete.");
    }

    private static void downloadFile(AmazonS3 s3Client, String bucketName, String key) throws IOException {
        System.out.println("Downloading " + key + " from S3 bucket " + bucketName);
        S3Object s3Object = s3Client.getObject(new GetObjectRequest(bucketName, key));
        InputStream objectData = s3Object.getObjectContent();
        // Process the objectData stream
        System.out.println("Content: " + IOUtils.toString(objectData));
        objectData.close();
        System.out.println("Download complete.");
    }

    private static String generatePresignedUrl(AmazonS3 s3Client, String bucketName, String key) {
        java.util.Date expiration = new java.util.Date();
        long expTimeMillis = expiration.getTime();
        expTimeMillis += 1000 * 60 * 10; // 10 minutes
        expiration.setTime(expTimeMillis);

        GeneratePresignedUrlRequest generatePresignedUrlRequest = new GeneratePresignedUrlRequest(bucketName, key)
                .withMethod(HttpMethod.GET)
                .withExpiration(expiration);

        URL url = s3Client.generatePresignedUrl(generatePresignedUrlRequest);
        return url.toString();
    }

    private static void multipartUpload(AmazonS3 s3Client, String bucketName, String key, File file) throws IOException {
        System.out.println("Initiating multipart upload for " + key + " to S3 bucket " + bucketName);

        // Step 1: Initialize multipart upload
        InitiateMultipartUploadRequest initRequest = new InitiateMultipartUploadRequest(bucketName, key);
        InitiateMultipartUploadResult initResponse = s3Client.initiateMultipartUpload(initRequest);
        String uploadId = initResponse.getUploadId();

        long contentLength = file.length();
        long partSize = 5 * 1024 * 1024; // 5 MB

        try {
            List<PartETag> partETags = new ArrayList<>();
            long filePosition = 0;
            for (int i = 1; filePosition < contentLength; i++) {
                partSize = Math.min(partSize, (contentLength - filePosition));

                UploadPartRequest uploadRequest = new UploadPartRequest()
                        .withBucketName(bucketName)
                        .withKey(key)
                        .withUploadId(uploadId)
                        .withPartNumber(i)
                        .withFileOffset(filePosition)
                        .withFile(file)
                        .withPartSize(partSize);

                UploadPartResult uploadResult = s3Client.uploadPart(uploadRequest);
                partETags.add(uploadResult.getPartETag());

                filePosition += partSize;
            }

            // Step 3: Complete the multipart upload
            CompleteMultipartUploadRequest compRequest = new CompleteMultipartUploadRequest(bucketName, key, uploadId, partETags);
            s3Client.completeMultipartUpload(compRequest);
            System.out.println("Multipart upload complete.");
        } catch (Exception e) {
            System.err.println("Multipart upload failed. Aborting upload.");
            s3Client.abortMultipartUpload(new AbortMultipartUploadRequest(bucketName, key, uploadId));
            throw new RuntimeException(e);
        }
    }
}
