# AWS S3 File Processing Service

This project demonstrates a file processing service with AWS S3 integration using the AWS Java SDK.

## Requirements

- Java 17 or higher
- Maven
- AWS Account with S3 bucket configured
- AWS credentials configured (e.g., via `~/.aws/credentials` file or environment variables)

## Installation

1.  Clone the repository.
2.  Navigate to the project directory.
3.  Build the project using Maven:

    ```bash
    mvn clean install
    ```

## Configuration

1.  **S3 Bucket Name**: Update the `BUCKET_NAME` constant in `S3FileService.java` with your actual S3 bucket name.
2.  **AWS Region**: Update the `CLIENT_REGION` constant in `S3FileService.java` with your desired AWS region.
3.  **AWS Credentials**: Ensure your AWS credentials are configured. The application uses `ProfileCredentialsProvider`, so you should have your credentials set up in `~/.aws/credentials` (Linux/macOS) or `C:\Users\USER_NAME\.aws\credentials` (Windows).

    Example `~/.aws/credentials`:

    ```
    [default]
    aws_access_key_id = YOUR_ACCESS_KEY_ID
    aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
    ```

## Usage

1.  Run the application:

    ```bash
    mvn exec:java
    ```

### Functionality

The application will perform the following operations:

-   **Upload File**: Uploads a `sample.txt` file to the specified S3 bucket.
-   **Download File**: Downloads `sample.txt` from the S3 bucket and prints its content.
-   **Generate Pre-signed URL**: Generates a pre-signed URL for `sample.txt` that is valid for 10 minutes, allowing temporary public access.
-   **Multipart Upload**: Demonstrates uploading a large file (`large_sample.txt` - 10MB) using multipart upload.
