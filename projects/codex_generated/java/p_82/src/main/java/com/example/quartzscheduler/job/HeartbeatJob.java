package com.example.quartzscheduler.job;

import java.time.Instant;

import org.quartz.DisallowConcurrentExecution;
import org.quartz.JobExecutionContext;
import org.quartz.JobExecutionException;
import org.quartz.PersistJobDataAfterExecution;
import org.springframework.scheduling.quartz.QuartzJobBean;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Cron-driven job that increments a counter persisted in Quartz's job store.
 */
@DisallowConcurrentExecution
@PersistJobDataAfterExecution
public class HeartbeatJob extends QuartzJobBean {

    private static final Logger logger = LoggerFactory.getLogger(HeartbeatJob.class);

    public static final String EXECUTION_COUNT = "executionCount";

    @Override
    protected void executeInternal(JobExecutionContext context) throws JobExecutionException {
        int current = context.getMergedJobDataMap().getInt(EXECUTION_COUNT);
        int next = current + 1;
        context.getJobDetail().getJobDataMap().put(EXECUTION_COUNT, next);

        logger.info("HeartbeatJob executed at {} (run #{})", Instant.now(), next);
    }
}
