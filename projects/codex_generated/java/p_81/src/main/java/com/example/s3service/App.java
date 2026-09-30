package com.example.s3service;

import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import software.amazon.awssdk.core.exception.SdkException;
import software.amazon.awssdk.regions.Region;

/**
 * Simple CLI wrapper around {@link S3FileService}. The CLI is intentionally minimal to keep the
 * sample focused on demonstrating the underlying service implementation.
 */
public final class App {

    private static final Logger logger = LoggerFactory.getLogger(App.class);

    private App() {
    }

    public static void main(String[] args) {
        List<String> params = new ArrayList<>();
        String regionName = System.getenv().getOrDefault("AWS_REGION", "us-east-1");

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            if (arg.startsWith("--region=")) {
                regionName = arg.substring("--region=".length());
            } else if ("--region".equals(arg)) {
                if (i + 1 >= args.length) {
                    System.err.println("Missing value after --region");
                    printUsage();
                    System.exit(1);
                }
                regionName = args[++i];
            } else {
                params.add(arg);
            }
        }

        if (params.isEmpty()) {
            printUsage();
            return;
        }

        String command = params.get(0);
        Region region = Region.of(regionName);

        try (S3FileService service = new S3FileService(region)) {
            switch (command) {
                case "upload" -> requireArgsAndRun(params, 4, () ->
                        service.uploadFile(params.get(1), params.get(2), Path.of(params.get(3))));
                case "download" -> requireArgsAndRun(params, 4, () ->
                        service.downloadFile(params.get(1), params.get(2), Path.of(params.get(3))));
                case "presign" -> requireArgsAndRun(params, 3, () -> {
                    Duration expiry = params.size() >= 4
                            ? Duration.ofSeconds(Long.parseLong(params.get(3)))
                            : Duration.ofMinutes(15);
                    var url = service.generatePresignedUrl(params.get(1), params.get(2), expiry);
                    System.out.println(url);
                });
                case "multipart-upload" -> requireArgsAndRun(params, 4, () ->
                        service.uploadLargeFile(params.get(1), params.get(2), Path.of(params.get(3))));
                default -> {
                    System.err.printf("Unknown command '%s'%n", command);
                    printUsage();
                    System.exit(1);
                }
            }
        } catch (SdkException e) {
            logger.error("AWS SDK error: {}", e.getMessage(), e);
            System.exit(2);
        } catch (IOException e) {
            logger.error("I/O error: {}", e.getMessage(), e);
            System.exit(3);
        } catch (IllegalArgumentException e) {
            logger.error(e.getMessage());
            System.exit(1);
        } catch (RuntimeException e) {
            logger.error("Unexpected error", e);
            System.exit(4);
        }
    }

    private static void requireArgsAndRun(List<String> params, int expected, CommandAction action) throws IOException {
        if (params.size() < expected) {
            printUsage();
            throw new IllegalArgumentException("Not enough arguments for command: " + params.get(0));
        }
        action.run();
    }

    @FunctionalInterface
    private interface CommandAction {
        void run() throws IOException;
    }

    private static void printUsage() {
        System.out.println("""
                Usage: java -jar s3-file-service-1.0.0.jar [--region <aws-region>] <command> [args...]

                Commands:
                  upload <bucket> <key> <file>            Upload a local file using a single PUT request
                  multipart-upload <bucket> <key> <file>  Upload large file with multipart upload
                  download <bucket> <key> <destination>   Download an object to local path
                  presign <bucket> <key> [seconds]        Generate presigned download URL (default 900 seconds)

                Region resolves in order: --region flag, AWS_REGION env var, defaults to us-east-1.
                AWS credentials are resolved with the default provider chain (env vars, profile, IMDS, etc.).
                """);
    }
}
