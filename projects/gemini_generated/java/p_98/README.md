# Distributed Lock Manager with Redisson

This project demonstrates a distributed lock manager using Spring Boot and Redisson.

## Requirements

- Java 8 or higher
- Maven
- Redis server running on `localhost:6379`

## How to Run

1. **Start Redis Server:**
   Ensure you have a Redis server running on `localhost:6379`. You can run it using Docker:
   ```bash
   docker run -d --name redis -p 6379:6379 redis
   ```

2. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd distributed-lock-manager
   ```

3. **Build the project:**
   ```bash
   mvn clean install
   ```

4. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start on port 8080.

## Usage

### Acquire a Lock

Access the following URL to acquire a regular distributed lock:

```bash
curl http://localhost:8080/lock
```

You can customize the lock name, wait time, and lease time:

```bash
curl "http://localhost:8080/lock?lockName=myCustomLock&waitTime=5&leaseTime=15"
```

### Acquire a Fair Lock

Access the following URL to acquire a fair distributed lock:

```bash
curl http://localhost:8080/fair-lock
```

You can customize the fair lock name, wait time, and lease time:

```bash
curl "http://localhost:8080/fair-lock?lockName=myCustomFairLock&waitTime=5&leaseTime=15"
```

### Testing Concurrency

To test the distributed locking, you can run multiple instances of the application or use multiple `curl` commands concurrently. For example, open two terminal windows and run:

**Terminal 1:**
```bash
curl http://localhost:8080/lock
```

**Terminal 2 (immediately after Terminal 1):**
```bash
curl http://localhost:8080/lock
```

You should observe that one request acquires the lock and the other waits or fails to acquire it, depending on the `waitTime` configured.
