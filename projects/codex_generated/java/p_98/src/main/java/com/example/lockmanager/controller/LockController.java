package com.example.lockmanager.controller;

import com.example.lockmanager.service.DistributedLockService;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import java.time.Duration;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/lock")
@Validated
public class LockController {

    private final DistributedLockService lockService;

    public LockController(DistributedLockService lockService) {
        this.lockService = lockService;
    }

    @PostMapping("/execute")
    public ResponseEntity<Map<String, Object>> execute(@RequestBody @Validated LockRequest request) {
        boolean success = lockService.withLock(
                request.getName(),
                request.isFair(),
                request.getWaitSeconds() == null ? null : Duration.ofSeconds(request.getWaitSeconds()),
                request.getLeaseSeconds() == null ? null : Duration.ofSeconds(request.getLeaseSeconds()),
                () -> {
                    try {
                        Thread.sleep(request.getExecutionMillis());
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
        );
        if (success) {
            return ResponseEntity.ok(Map.of("status", "executed", "lock", request.getName()));
        }
        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("status", "lock_failed", "lock", request.getName()));
    }

    public static class LockRequest {
        @NotBlank
        private String name;
        private boolean fair;
        @Min(0)
        private Long waitSeconds;
        @Min(1)
        private Long leaseSeconds;
        @Min(0)
        private long executionMillis = 1000;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public boolean isFair() {
            return fair;
        }

        public void setFair(boolean fair) {
            this.fair = fair;
        }

        public Long getWaitSeconds() {
            return waitSeconds;
        }

        public void setWaitSeconds(Long waitSeconds) {
            this.waitSeconds = waitSeconds;
        }

        public Long getLeaseSeconds() {
            return leaseSeconds;
        }

        public void setLeaseSeconds(Long leaseSeconds) {
            this.leaseSeconds = leaseSeconds;
        }

        public long getExecutionMillis() {
            return executionMillis;
        }

        public void setExecutionMillis(long executionMillis) {
            this.executionMillis = executionMillis;
        }
    }
}
