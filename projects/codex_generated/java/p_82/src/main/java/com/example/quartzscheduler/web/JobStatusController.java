package com.example.quartzscheduler.web;

import com.example.quartzscheduler.job.HeartbeatJob;
import java.util.HashMap;
import java.util.Map;

import org.quartz.JobDetail;
import org.quartz.SchedulerException;
import org.quartz.Scheduler;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Simple REST endpoint to inspect the persisted job data.
 */
@RestController
public class JobStatusController {

    private final Scheduler scheduler;

    public JobStatusController(Scheduler scheduler) {
        this.scheduler = scheduler;
    }

    @GetMapping("/api/heartbeat")
    public ResponseEntity<Map<String, Object>> heartbeatStatus() throws SchedulerException {
        JobDetail detail = scheduler.getJobDetail(org.quartz.JobKey.jobKey("heartbeatJob"));
        if (detail == null) {
            return ResponseEntity.notFound().build();
        }
        Map<String, Object> payload = new HashMap<>();
        payload.put("jobKey", detail.getKey().toString());
        payload.put("nextFireTime", scheduler.getTriggersOfJob(detail.getKey())
                .stream()
                .map(trigger -> trigger.getNextFireTime())
                .findFirst()
                .orElse(null));
        payload.put("executionCount", detail.getJobDataMap().getInt(HeartbeatJob.EXECUTION_COUNT));
        return ResponseEntity.ok(payload);
    }
}
