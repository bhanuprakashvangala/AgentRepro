package com.example.logging.audit;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Logs audit events using the dedicated audit logger defined in log4j2.xml.
 */
public class AuditService {

    private static final Logger auditLogger = LogManager.getLogger("com.example.logging.audit");

    public void recordLoginEvent(String userEmail) {
        auditLogger.info("User login: {}", userEmail);
    }

    public void recordDataExport(String filename, int recordCount) {
        auditLogger.info("Data export completed: file={} records={}", filename, recordCount);
    }
}
