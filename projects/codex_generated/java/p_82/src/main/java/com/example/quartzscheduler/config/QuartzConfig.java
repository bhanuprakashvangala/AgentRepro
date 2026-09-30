package com.example.quartzscheduler.config;

import com.example.quartzscheduler.job.HeartbeatJob;
import org.quartz.JobBuilder;
import org.quartz.JobDetail;
import org.quartz.Trigger;
import org.quartz.TriggerBuilder;
import org.quartz.CronScheduleBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Registers Quartz job and trigger beans so Spring Boot auto-wires them into the scheduler.
 */
@Configuration
public class QuartzConfig {

    @Value("${scheduler.heartbeat.cron:0 0/1 * * * ?}")
    private String cronExpression;

    @Bean
    public JobDetail heartbeatJobDetail() {
        return JobBuilder.newJob(HeartbeatJob.class)
                .withIdentity("heartbeatJob")
                .usingJobData(HeartbeatJob.EXECUTION_COUNT, 0)
                .storeDurably()
                .build();
    }

    @Bean
    public Trigger heartbeatTrigger(JobDetail heartbeatJobDetail) {
        return TriggerBuilder.newTrigger()
                .forJob(heartbeatJobDetail)
                .withIdentity("heartbeatTrigger")
                .withSchedule(CronScheduleBuilder.cronSchedule(cronExpression))
                .build();
    }
}
