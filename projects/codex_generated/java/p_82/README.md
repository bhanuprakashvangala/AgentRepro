# Spring Boot Quartz Scheduler

Cron-based scheduled task runner built with Spring Boot and Quartz. Jobs are persisted in an H2 file database so execution state survives restarts.

## Features
- Quartz scheduler configured with JDBC job store (`spring.quartz.job-store-type=jdbc`)
- Cron-triggered job (`HeartbeatJob`) that runs on a configurable schedule and keeps an execution counter in the job data map
- REST endpoint (`/api/heartbeat`) to inspect current job state and next fire time
- H2 file database initialized automatically for Quartz schema and data persistence

## Prerequisites
- Java 17 or later
- Apache Maven 3.9+

## Setup & Run
```bash
cd 1-GPT/p_82
mvn clean package
mvn spring-boot:run
```

By default the heartbeat job executes every minute (`scheduler.heartbeat.cron=0 0/1 * * * ?`). Adjust the cron expression in `src/main/resources/application.properties` if needed.

## Verify
Once the application starts on port 8080:
1. Call the heartbeat status endpoint:
   ```bash
   curl http://localhost:8080/api/heartbeat
   ```
   You should see the persisted execution counter increment with each run.
2. (Optional) Inspect the Quartz tables through the H2 console at http://localhost:8080/h2-console  
   - JDBC URL: `jdbc:h2:file:./quartz-db`
   - User: `sa`
   - Password: *(empty)*

## Persistence
The job store uses the on-disk H2 database located at `./quartz-db.mv.db`. Stop the app with `Ctrl+C`; when you restart it, Quartz loads the job and its execution counter from the previous session.
