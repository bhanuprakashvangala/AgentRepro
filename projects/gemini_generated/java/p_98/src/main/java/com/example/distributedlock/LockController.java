package com.example.distributedlock;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LockController {

    private final LockService lockService;

    @Autowired
    public LockController(LockService lockService) {
        this.lockService = lockService;
    }

    @GetMapping("/lock")
    public ResponseEntity<String> acquireLock(
            @RequestParam(defaultValue = "myLock") String lockName,
            @RequestParam(defaultValue = "10") long waitTime,
            @RequestParam(defaultValue = "30") long leaseTime
    ) {
        String result = lockService.doSomethingWithLock(lockName, waitTime, leaseTime);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/fair-lock")
    public ResponseEntity<String> acquireFairLock(
            @RequestParam(defaultValue = "myFairLock") String lockName,
            @RequestParam(defaultValue = "10") long waitTime,
            @RequestParam(defaultValue = "30") long leaseTime
    ) {
        String result = lockService.doSomethingWithFairLock(lockName, waitTime, leaseTime);
        return ResponseEntity.ok(result);
    }
}
