package com.example.logging.service;

import java.time.Duration;
import java.util.Random;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Emits log messages across different levels to demonstrate routing to appenders.
 */
public class DiagnosticService {

    private static final Logger logger = LogManager.getLogger(DiagnosticService.class);
    private final Random random = new Random();

    public void simulateDiagnostics() throws InterruptedException {
        logger.info("Running diagnostics across {} modules", 5);
        for (int i = 1; i <= 5; i++) {
            logger.debug("Module {} heartbeat OK", i);
            if (random.nextBoolean()) {
                logger.warn("Module {} reported elevated latency: {} ms", i, randomLatency());
            }
        }
        logger.info("Diagnostics complete");
    }

    public void invokeRiskyOperation() {
        logger.info("Invoking risky operation");
        if (random.nextBoolean()) {
            throw new IllegalStateException("Simulated failure triggered by DiagnosticService");
        }
        logger.info("Risky operation completed successfully");
    }

    private long randomLatency() {
        return Duration.ofMillis(100 + random.nextInt(900)).toMillis();
    }
}
