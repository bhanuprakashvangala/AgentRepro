package com.example.resilience;

import io.github.resilience4j.circuitbreaker.*;
import io.github.resilience4j.retry.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

// Custom Retry Policy
class RetryPolicy {
    private final int maxAttempts;
    private final long initialDelayMs;
    private final double multiplier;
    private final long maxDelayMs;

    public RetryPolicy(int maxAttempts, long initialDelayMs, double multiplier, long maxDelayMs) {
        this.maxAttempts = maxAttempts;
        this.initialDelayMs = initialDelayMs;
        this.multiplier = multiplier;
        this.maxDelayMs = maxDelayMs;
    }

    public <T> T execute(Supplier<T> operation) {
        int attempt = 0;
        Exception lastException = null;

        while (attempt < maxAttempts) {
            try {
                return operation.get();
            } catch (Exception e) {
                lastException = e;
                attempt++;

                if (attempt < maxAttempts) {
                    long delay = calculateDelay(attempt);
                    System.out.println("  Attempt " + attempt + " failed. Retrying in " + delay + "ms...");

                    try {
                        Thread.sleep(delay);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException("Retry interrupted", ie);
                    }
                }
            }
        }

        throw new RuntimeException("Operation failed after " + maxAttempts + " attempts", lastException);
    }

    private long calculateDelay(int attempt) {
        long delay = (long) (initialDelayMs * Math.pow(multiplier, attempt - 1));
        return Math.min(delay, maxDelayMs);
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private int maxAttempts = 3;
        private long initialDelayMs = 1000;
        private double multiplier = 2.0;
        private long maxDelayMs = 30000;

        public Builder maxAttempts(int maxAttempts) {
            this.maxAttempts = maxAttempts;
            return this;
        }

        public Builder initialDelay(long initialDelayMs) {
            this.initialDelayMs = initialDelayMs;
            return this;
        }

        public Builder multiplier(double multiplier) {
            this.multiplier = multiplier;
            return this;
        }

        public Builder maxDelay(long maxDelayMs) {
            this.maxDelayMs = maxDelayMs;
            return this;
        }

        public RetryPolicy build() {
            return new RetryPolicy(maxAttempts, initialDelayMs, multiplier, maxDelayMs);
        }
    }
}

// Custom Circuit Breaker
class SimpleCircuitBreaker {
    private enum State { CLOSED, OPEN, HALF_OPEN }

    private State state = State.CLOSED;
    private final int failureThreshold;
    private final long timeoutMs;
    private int failureCount = 0;
    private int successCount = 0;
    private long openedAt = 0;

    public SimpleCircuitBreaker(int failureThreshold, long timeoutMs) {
        this.failureThreshold = failureThreshold;
        this.timeoutMs = timeoutMs;
    }

    public synchronized <T> T execute(Supplier<T> operation) {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - openedAt >= timeoutMs) {
                System.out.println("  Circuit breaker transitioning to HALF_OPEN");
                state = State.HALF_OPEN;
                successCount = 0;
            } else {
                throw new RuntimeException("Circuit breaker is OPEN");
            }
        }

        try {
            T result = operation.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            throw e;
        }
    }

    private void onSuccess() {
        if (state == State.HALF_OPEN) {
            successCount++;
            if (successCount >= 2) {
                System.out.println("  Circuit breaker transitioning to CLOSED");
                state = State.CLOSED;
                failureCount = 0;
            }
        } else if (state == State.CLOSED) {
            failureCount = 0;
        }
    }

    private void onFailure() {
        failureCount++;
        if (failureCount >= failureThreshold) {
            System.out.println("  Circuit breaker transitioning to OPEN");
            state = State.OPEN;
            openedAt = System.currentTimeMillis();
        }
    }

    public State getState() {
        return state;
    }

    public void reset() {
        state = State.CLOSED;
        failureCount = 0;
        successCount = 0;
        openedAt = 0;
    }
}

// Fallback Handler
interface FallbackHandler<T> {
    T handle(Exception e);
}

class ResilientOperation<T> {
    private final Supplier<T> operation;
    private RetryPolicy retryPolicy;
    private SimpleCircuitBreaker circuitBreaker;
    private FallbackHandler<T> fallbackHandler;

    public ResilientOperation(Supplier<T> operation) {
        this.operation = operation;
    }

    public ResilientOperation<T> withRetry(RetryPolicy policy) {
        this.retryPolicy = policy;
        return this;
    }

    public ResilientOperation<T> withCircuitBreaker(SimpleCircuitBreaker breaker) {
        this.circuitBreaker = breaker;
        return this;
    }

    public ResilientOperation<T> withFallback(FallbackHandler<T> handler) {
        this.fallbackHandler = handler;
        return this;
    }

    public T execute() {
        try {
            Supplier<T> wrappedOperation = operation;

            if (circuitBreaker != null) {
                wrappedOperation = () -> circuitBreaker.execute(operation);
            }

            if (retryPolicy != null) {
                return retryPolicy.execute(wrappedOperation);
            }

            return wrappedOperation.get();

        } catch (Exception e) {
            if (fallbackHandler != null) {
                System.out.println("  Executing fallback handler");
                return fallbackHandler.handle(e);
            }
            throw e;
        }
    }
}

// Mock unstable service
class UnstableService {
    private final AtomicInteger callCount = new AtomicInteger(0);
    private final double failureRate;

    public UnstableService(double failureRate) {
        this.failureRate = failureRate;
    }

    public String call() {
        int count = callCount.incrementAndGet();
        System.out.println("  Service call #" + count);

        if (Math.random() < failureRate) {
            throw new RuntimeException("Service temporarily unavailable");
        }

        return "Success: Call #" + count;
    }

    public void reset() {
        callCount.set(0);
    }
}

public class ResiliencePatternsApp {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Resilience Patterns Demo ===\n");

        // Example 1: Basic Retry with Exponential Backoff
        System.out.println("--- Example 1: Retry with Exponential Backoff ---");

        RetryPolicy retryPolicy = RetryPolicy.builder()
            .maxAttempts(3)
            .initialDelay(100)
            .multiplier(2.0)
            .build();

        UnstableService unstableService = new UnstableService(0.7); // 70% failure rate

        try {
            String result = retryPolicy.execute(() -> unstableService.call());
            System.out.println("Result: " + result);
        } catch (Exception e) {
            System.out.println("Operation failed: " + e.getMessage());
        }

        // Example 2: Circuit Breaker
        System.out.println("\n--- Example 2: Circuit Breaker Pattern ---");

        SimpleCircuitBreaker circuitBreaker = new SimpleCircuitBreaker(3, 2000);
        UnstableService veryUnstableService = new UnstableService(0.9); // 90% failure rate

        for (int i = 0; i < 10; i++) {
            System.out.println("\nAttempt " + (i + 1) + ":");
            try {
                String result = circuitBreaker.execute(() -> veryUnstableService.call());
                System.out.println("  Result: " + result);
            } catch (Exception e) {
                System.out.println("  Failed: " + e.getMessage());
            }
            System.out.println("  Circuit breaker state: " + circuitBreaker.getState());

            Thread.sleep(500);
        }

        // Example 3: Retry + Circuit Breaker
        System.out.println("\n--- Example 3: Retry + Circuit Breaker ---");

        circuitBreaker.reset();
        UnstableService moderateService = new UnstableService(0.5); // 50% failure rate

        ResilientOperation<String> resilientOp = new ResilientOperation<>(() -> moderateService.call())
            .withRetry(retryPolicy)
            .withCircuitBreaker(circuitBreaker);

        for (int i = 0; i < 5; i++) {
            System.out.println("\nOperation " + (i + 1) + ":");
            try {
                String result = resilientOp.execute();
                System.out.println("Result: " + result);
            } catch (Exception e) {
                System.out.println("Failed: " + e.getMessage());
            }
            Thread.sleep(300);
        }

        // Example 4: Fallback Handler
        System.out.println("\n--- Example 4: Fallback Handler ---");

        UnstableService alwaysFailingService = new UnstableService(1.0); // 100% failure

        ResilientOperation<String> withFallback = new ResilientOperation<>(() -> alwaysFailingService.call())
            .withRetry(RetryPolicy.builder().maxAttempts(2).initialDelay(50).build())
            .withFallback(e -> {
                System.out.println("  Fallback triggered: " + e.getMessage());
                return "Fallback response: Using cached data";
            });

        String result = withFallback.execute();
        System.out.println("Final result: " + result);

        // Example 5: Resilience4j Circuit Breaker
        System.out.println("\n--- Example 5: Resilience4j Circuit Breaker ---");

        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .slidingWindowSize(5)
            .failureRateThreshold(50.0f)
            .waitDurationInOpenState(Duration.ofSeconds(2))
            .build();

        CircuitBreaker r4jCircuitBreaker = CircuitBreaker.of("myService", config);

        // Add event listeners
        r4jCircuitBreaker.getEventPublisher()
            .onStateTransition(event ->
                System.out.println("  State transition: " + event.getStateTransition()));

        UnstableService r4jService = new UnstableService(0.6);

        for (int i = 0; i < 10; i++) {
            System.out.println("\nCall " + (i + 1) + ":");
            try {
                String res = r4jCircuitBreaker.executeSupplier(() -> r4jService.call());
                System.out.println("  Success: " + res);
            } catch (Exception e) {
                System.out.println("  Failed: " + e.getMessage());
            }
            System.out.println("  State: " + r4jCircuitBreaker.getState());
            Thread.sleep(300);
        }

        // Example 6: Resilience4j Retry
        System.out.println("\n--- Example 6: Resilience4j Retry ---");

        RetryConfig retryConfig = RetryConfig.custom()
            .maxAttempts(3)
            .waitDuration(Duration.ofMillis(500))
            .retryExceptions(RuntimeException.class)
            .build();

        Retry retry = Retry.of("myRetry", retryConfig);

        retry.getEventPublisher()
            .onRetry(event ->
                System.out.println("  Retry attempt " + event.getNumberOfRetryAttempts()));

        UnstableService retryService = new UnstableService(0.5);

        try {
            String retryResult = retry.executeSupplier(() -> retryService.call());
            System.out.println("Result: " + retryResult);
        } catch (Exception e) {
            System.out.println("Failed after retries: " + e.getMessage());
        }

        // Example 7: Combined Retry + Circuit Breaker (Resilience4j)
        System.out.println("\n--- Example 7: Combined Patterns (Resilience4j) ---");

        CircuitBreaker combinedCB = CircuitBreaker.of("combined", config);
        Retry combinedRetry = Retry.of("combined", retryConfig);

        UnstableService combinedService = new UnstableService(0.4);

        Supplier<String> decoratedSupplier = combinedCB.decorateSupplier(
            Retry.decorateSupplier(combinedRetry, () -> combinedService.call())
        );

        for (int i = 0; i < 5; i++) {
            System.out.println("\nCombined operation " + (i + 1) + ":");
            try {
                String combinedResult = decoratedSupplier.get();
                System.out.println("  Success: " + combinedResult);
            } catch (Exception e) {
                System.out.println("  Failed: " + e.getMessage());
            }
            Thread.sleep(500);
        }

        System.out.println("\n=== Resilience Patterns Demo Complete ===");
        System.out.println("\nImplemented Patterns:");
        System.out.println("  ✓ Retry with exponential backoff");
        System.out.println("  ✓ Circuit breaker (CLOSED/OPEN/HALF_OPEN)");
        System.out.println("  ✓ Fallback handlers");
        System.out.println("  ✓ Combined resilience strategies");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Configurable retry policies");
        System.out.println("  ✓ Failure threshold management");
        System.out.println("  ✓ Automatic recovery");
        System.out.println("  ✓ State transition events");
        System.out.println("  ✓ Graceful degradation");
    }
}
