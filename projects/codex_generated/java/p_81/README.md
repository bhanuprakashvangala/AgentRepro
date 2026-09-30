# S3 File Processing Service

Command-line utility and reusable service layer for uploading, downloading, and sharing files stored in Amazon S3. Supports standard PUT uploads, multipart uploads for large files, downloads, and presigned URL generation.

## Features
- Uses AWS SDK for Java v2 with the default credentials provider chain.
- Upload small files via single PUT requests.
- Upload large files with multipart transfer acceleration through `S3TransferManager`.
- Download objects to local paths with automatic directory creation.
- Generate time-bound presigned URLs for secure sharing.

## Prerequisites
- Java Development Kit (JDK) 17 or newer
- Apache Maven 3.9+ installed and available on the `PATH`
- An AWS account with access to the target S3 bucket
- AWS credentials configured (environment variables, `~/.aws/credentials`, or any other method supported by the default credentials provider chain)

You can optionally set the region with the `AWS_REGION` environment variable or the `--region` CLI flag. If omitted, the application defaults to `us-east-1`.

## Build
```bash
cd 1-GPT/p_81
mvn clean package
```
The shaded artifact is **not** produced; run with the standard Maven target JAR:
```
target/s3-file-service-1.0.0.jar
```

## Usage
Run the CLI with:
```bash
java -jar target/s3-file-service-1.0.0.jar [--region <aws-region>] <command> [args...]
```

Supported commands:
- `upload <bucket> <key> <file>` – Uploads a local file with a single PUT request.
- `multipart-upload <bucket> <key> <file>` – Uses multipart uploads suitable for large files (recommended for files >100 MB).
- `download <bucket> <key> <destination>` – Downloads an object to the specified local path (directories are created automatically).
- `presign <bucket> <key> [seconds]` – Prints a presigned URL valid for the given duration (default 900 seconds).

Examples:
```bash
# Upload using default region/us-east-1
java -jar target/s3-file-service-1.0.0.jar upload my-bucket backups/data.zip ./data.zip

# Multipart upload with explicit region
java -jar target/s3-file-service-1.0.0.jar --region eu-west-1 multipart-upload my-bucket large/video.mp4 ./video.mp4

# Download a file
java -jar target/s3-file-service-1.0.0.jar download my-bucket reports/report.csv ./downloads/report.csv

# Generate a 10 minute presigned URL
java -jar target/s3-file-service-1.0.0.jar presign my-bucket backups/data.zip 600
```

## Cleanup
No additional resources are created besides the objects uploaded to S3. Delete those objects in S3 when they are no longer needed.
