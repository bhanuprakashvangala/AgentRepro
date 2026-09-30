# Log4j2 Logging Framework Demo

Standalone Java application that showcases a Log4j2 configuration with multiple appenders, per-logger routing, and size-based rolling policies.

## Features
- Console appender (human-readable pattern)
- File appender for audit events
- Rolling file appender with 10 MB size-based rotation (gzipped archives, keeps 20)
- Separate audit logger (`com.example.logging.audit`) targeting only the file appender
- Demonstration services emitting logs across INFO, WARN, ERROR, DEBUG levels

## Prerequisites
- Java 17 or later
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_88
mvn clean package
mvn exec:java -Dexec.mainClass=com.example.logging.LoggingDemoApplication
```
> If `mvn exec:java` is unavailable, run the class directly: `java -cp target/log4j2-framework-1.0.0.jar:target/libs/* com.example.logging.LoggingDemoApplication`

The first run creates a `logs/` directory with:
- `log4j2-framework.log` (regular file appender)
- `log4j2-framework-rolling.log` (active rolling log)
- archived files in `logs/archive/` as rotation occurs

## Adjusting Log Levels
- Edit `src/main/resources/log4j2.xml` and change the `<Root level="info">` element to `debug` (or another level) to enable additional verbosity.
- Per-package overrides can be added by inserting additional `<Logger>` elements.

## What to Look For
- Console: shows INFO/WARN/ERROR entries.
- `log4j2-framework.log`: contains audit entries only (login, data export).
- `log4j2-framework-rolling.log`: aggregates application logs with automatic rotation at ~10 MB.

## Cleanup
Remove generated logs:
```bash
rm -rf logs
```
