package com.example.lockmanager.service;

import java.time.Duration;
import java.util.concurrent.TimeUnit;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class DistributedLockService {

    private static final Logger logger = LoggerFactory.getLogger(DistributedLockService.class);

    private final RedissonClient redissonClient;

    public DistributedLockService(RedissonClient redissonClient) {
        this.redissonClient = redissonClient;
    }

    public boolean withLock(String lockName, boolean fair, Duration waitTime, Duration leaseTime, Runnable task) {
        RLock lock = fair ? redissonClient.getFairLock(lockName) : redissonClient.getLock(lockName);
        long wait = waitTime == null ? 5 : waitTime.toSeconds();
        long lease = leaseTime == null ? 30 : leaseTime.toSeconds();
        boolean acquired = false;
        try {
            acquired = lock.tryLock(wait, lease, TimeUnit.SECONDS);
            if (!acquired) {
                logger.warn("Failed to acquire lock {} within {} seconds", lockName, wait);
                return false;
            }
            task.run();
            return true;
        } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            logger.error("Interrupted while waiting for lock {}", lockName, ie);
            return false;
        } catch (Exception ex) {
            logger.error("Error executing task under lock {}", lockName, ex);
            return false;
        } finally {
            if (acquired && lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
