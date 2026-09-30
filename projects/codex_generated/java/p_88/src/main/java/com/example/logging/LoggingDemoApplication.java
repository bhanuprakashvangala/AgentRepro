package com.example.logging;

import com.example.logging.audit.AuditService;
import com.example.logging.service.DiagnosticService;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Entry point for the Log4j2 demo. Demonstrates multiple appenders, log levels, and rolling policies.
 */
public final class LoggingDemoApplication {

    private static final Logger logger = LogManager.getLogger(LoggingDemoApplication.class);

    private LoggingDemoApplication() {
    }

    public static void main(String[] args) throws Exception {
        ensureLogDir();

        logger.info("Starting Log4j2 demonstration application");
        logger.debug("Debug logging is disabled by default; adjust log4j2.xml to enable");

        DiagnosticService diagnosticService = new DiagnosticService();
        diagnosticService.simulateDiagnostics();

        AuditService auditService = new AuditService();
        auditService.recordLoginEvent("carol@example.com");
        auditService.recordDataExport("export-2024-Q2.csv", 42);

        logger.warn("Warnings are visible in console and rolling file");
        try {
            diagnosticService.invokeRiskyOperation();
        } catch (IllegalStateException ex) {
            logger.error("Caught exception from risky operation", ex);
        }

        logger.info("Application finished. Check the logs directory for generated files.");
    }

    private static void ensureLogDir() throws Exception {
        Path logDir = Path.of("logs");
        if (Files.notExists(logDir)) {
            Files.createDirectories(logDir);
            logger.trace("Created log directory at {}", logDir.toAbsolutePath());
        }
    }
}
