# Spring Batch Processing Job

This project is a batch processing job using Spring Batch to read data from a CSV file, process it, and write it to a MySQL database.

## Requirements

- Java 17 or higher
- Maven
- MySQL database

## Database Setup

1.  Create a MySQL database named `spring_batch_db`.
2.  Create a user `myuser` with password `mypassword` and grant all privileges to `spring_batch_db`.

## Installation

1.  Clone the repository.
2.  Navigate to the project directory.
3.  Build the project using Maven:

    ```bash
    mvn clean install
    ```

## Usage

1.  Place your `users.csv` file in the `src/main/resources` directory.
2.  Run the Spring Boot application:

    ```bash
    mvn spring-boot:run
    ```

3.  The batch job will automatically start, read data from `users.csv`, process it (converting name to uppercase and email to lowercase), and write it to the `user` table in your MySQL database.

### Retry Logic

The `UserProcessor` includes a simulated failure for users named "Jane Smith". The batch job is configured with retry logic to attempt processing failed items up to 3 times.
