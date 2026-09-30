package com.example.distributedlock;

import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class LockService {

    private final RedissonClient redissonClient;

    @Autowired
    public LockService(RedissonClient redissonClient) {
        this.redissonClient = redissonClient;
    }

    public String doSomethingWithLock(String lockName, long waitTime, long leaseTime) {
        RLock lock = redissonClient.getLock(lockName);
        try {
            boolean acquired = lock.tryLock(waitTime, leaseTime, TimeUnit.SECONDS);
            if (acquired) {
                try {
                    // Simulate some work
                    Thread.sleep(2000);
                    return "Lock '" + lockName + "' acquired and released successfully.";
                } finally {
                    lock.unlock();
                }
            } else {
                return "Could not acquire lock '" + lockName + "'. Another instance holds the lock.";
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return "Interrupted while trying to acquire lock '" + lockName + "'.";
        }
    }

    public String doSomethingWithFairLock(String lockName, long waitTime, long leaseTime) {
        RLock fairLock = redissonClient.getFairLock(lockName);
        try {
            boolean acquired = fairLock.tryLock(waitTime, leaseTime, TimeUnit.SECONDS);
            if (acquired) {
                try {
                    // Simulate some work
                    Thread.sleep(2000);
                    return "Fair Lock '" + lockName + "' acquired and released successfully.";
                } finally {
                    fairLock.unlock();
                }
            } else {
                return "Could not acquire fair lock '" + lockName + "'. Another instance holds the lock.";
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return "Interrupted while trying to acquire fair lock '" + lockName + "'.";
        }
    }
}
