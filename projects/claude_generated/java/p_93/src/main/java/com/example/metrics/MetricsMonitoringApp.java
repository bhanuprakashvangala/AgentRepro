package com.example.metrics;

import com.codahale.metrics.*;
import com.codahale.metrics.jvm.*;
import java.lang.management.ManagementFactory;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.*;

class MetricsManager {
    private final MetricRegistry registry;
    private final ScheduledExecutorService reporter;

    public MetricsManager() {
        this.registry = new MetricRegistry();
        this.reporter = Executors.newSingleThreadScheduledExecutor();

        // Register JVM metrics
        registerJvmMetrics();
    }

    private void registerJvmMetrics() {
        registry.register("jvm.memory", new MemoryUsageGaugeSet());
        registry.register("jvm.gc", new GarbageCollectorMetricSet());
        registry.register("jvm.threads", new ThreadStatesGaugeSet());
        registry.register("jvm.files", new FileDescriptorRatioGauge());
    }

    public Counter getCounter(String name) {
        return registry.counter(name);
    }

    public Meter getMeter(String name) {
        return registry.meter(name);
    }

    public Histogram getHistogram(String name) {
        return registry.histogram(name);
    }

    public Timer getTimer(String name) {
        return registry.timer(name);
    }

    public <T> void registerGauge(String name, Gauge<T> gauge) {
        registry.register(name, gauge);
    }

    public MetricRegistry getRegistry() {
        return registry;
    }

    public void startConsoleReporter(long period, TimeUnit unit) {
        ConsoleReporter consoleReporter = ConsoleReporter.forRegistry(registry)
            .convertRatesTo(TimeUnit.SECONDS)
            .convertDurationsTo(TimeUnit.MILLISECONDS)
            .build();

        reporter.scheduleAtFixedRate(consoleReporter::report, period, period, unit);
    }

    public Map<String, Object> getMetricsSnapshot() {
        Map<String, Object> snapshot = new HashMap<>();

        registry.getCounters().forEach((name, counter) ->
            snapshot.put(name, Map.of("type", "counter", "count", counter.getCount()))
        );

        registry.getMeters().forEach((name, meter) ->
            snapshot.put(name, Map.of(
                "type", "meter",
                "count", meter.getCount(),
                "meanRate", meter.getMeanRate(),
                "oneMinuteRate", meter.getOneMinuteRate()
            ))
        );

        registry.getHistograms().forEach((name, histogram) -> {
            Snapshot snap = histogram.getSnapshot();
            snapshot.put(name, Map.of(
                "type", "histogram",
                "count", histogram.getCount(),
                "min", snap.getMin(),
                "max", snap.getMax(),
                "mean", snap.getMean(),
                "median", snap.getMedian(),
                "p95", snap.get95thPercentile(),
                "p99", snap.get99thPercentile()
            ));
        });

        registry.getTimers().forEach((name, timer) -> {
            Snapshot snap = timer.getSnapshot();
            snapshot.put(name, Map.of(
                "type", "timer",
                "count", timer.getCount(),
                "meanRate", timer.getMeanRate(),
                "mean", snap.getMean(),
                "median", snap.getMedian(),
                "p95", snap.get95thPercentile()
            ));
        });

        return snapshot;
    }

    public void shutdown() {
        reporter.shutdown();
    }
}

class ApplicationMetrics {
    private final MetricsManager metricsManager;

    // Counters
    private final Counter requestCounter;
    private final Counter errorCounter;
    private final Counter successCounter;

    // Meters
    private final Meter requestRate;
    private final Meter errorRate;

    // Histograms
    private final Histogram responseSizeHistogram;
    private final Histogram queueSizeHistogram;

    // Timers
    private final Timer requestTimer;
    private final Timer databaseQueryTimer;

    public ApplicationMetrics(MetricsManager metricsManager) {
        this.metricsManager = metricsManager;

        // Initialize metrics
        this.requestCounter = metricsManager.getCounter("app.requests.total");
        this.errorCounter = metricsManager.getCounter("app.requests.errors");
        this.successCounter = metricsManager.getCounter("app.requests.success");

        this.requestRate = metricsManager.getMeter("app.requests.rate");
        this.errorRate = metricsManager.getMeter("app.errors.rate");

        this.responseSizeHistogram = metricsManager.getHistogram("app.response.size");
        this.queueSizeHistogram = metricsManager.getHistogram("app.queue.size");

        this.requestTimer = metricsManager.getTimer("app.request.duration");
        this.databaseQueryTimer = metricsManager.getTimer("app.database.query.duration");
    }

    public void recordRequest(boolean success, long responseSizeBytes, long durationMs) {
        requestCounter.inc();
        requestRate.mark();

        if (success) {
            successCounter.inc();
        } else {
            errorCounter.inc();
            errorRate.mark();
        }

        responseSizeHistogram.update(responseSizeBytes);
        requestTimer.update(durationMs, TimeUnit.MILLISECONDS);
    }

    public void recordDatabaseQuery(long durationMs) {
        databaseQueryTimer.update(durationMs, TimeUnit.MILLISECONDS);
    }

    public void recordQueueSize(int size) {
        queueSizeHistogram.update(size);
    }

    public Timer.Context startRequestTimer() {
        return requestTimer.time();
    }

    public Timer.Context startDatabaseTimer() {
        return databaseQueryTimer.time();
    }
}

class HealthCheck {
    private final String name;
    private final Callable<Boolean> checker;

    public HealthCheck(String name, Callable<Boolean> checker) {
        this.name = name;
        this.checker = checker;
    }

    public HealthCheckResult check() {
        try {
            boolean healthy = checker.call();
            return new HealthCheckResult(name, healthy, healthy ? "OK" : "Unhealthy", null);
        } catch (Exception e) {
            return new HealthCheckResult(name, false, "Check failed", e.getMessage());
        }
    }

    public String getName() {
        return name;
    }
}

record HealthCheckResult(String name, boolean healthy, String message, String error) {
    @Override
    public String toString() {
        return String.format("%s: %s - %s%s",
            name,
            healthy ? "HEALTHY" : "UNHEALTHY",
            message,
            error != null ? " (" + error + ")" : ""
        );
    }
}

class HealthCheckRegistry {
    private final Map<String, HealthCheck> healthChecks = new ConcurrentHashMap<>();

    public void register(HealthCheck healthCheck) {
        healthChecks.put(healthCheck.getName(), healthCheck);
    }

    public Map<String, HealthCheckResult> runAllChecks() {
        Map<String, HealthCheckResult> results = new HashMap<>();
        healthChecks.forEach((name, check) -> results.put(name, check.check()));
        return results;
    }

    public boolean isHealthy() {
        return runAllChecks().values().stream()
            .allMatch(HealthCheckResult::healthy);
    }
}

class SystemMonitor {
    private final MetricsManager metricsManager;
    private final ScheduledExecutorService scheduler;

    public SystemMonitor(MetricsManager metricsManager) {
        this.metricsManager = metricsManager;
        this.scheduler = Executors.newSingleThreadScheduledExecutor();

        registerSystemGauges();
    }

    private void registerSystemGauges() {
        // CPU Usage
        metricsManager.registerGauge("system.cpu.usage", () ->
            ManagementFactory.getOperatingSystemMXBean().getSystemLoadAverage()
        );

        // Memory Usage
        metricsManager.registerGauge("system.memory.used", () -> {
            Runtime runtime = Runtime.getRuntime();
            return runtime.totalMemory() - runtime.freeMemory();
        });

        metricsManager.registerGauge("system.memory.free", () ->
            Runtime.getRuntime().freeMemory()
        );

        metricsManager.registerGauge("system.memory.max", () ->
            Runtime.getRuntime().maxMemory()
        );

        // Thread Count
        metricsManager.registerGauge("system.threads.count", () ->
            Thread.activeCount()
        );
    }

    public void startMonitoring(long interval, TimeUnit unit) {
        scheduler.scheduleAtFixedRate(this::collectMetrics, 0, interval, unit);
    }

    private void collectMetrics() {
        // Additional custom metric collection can be added here
    }

    public void shutdown() {
        scheduler.shutdown();
    }
}

public class MetricsMonitoringApp {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Metrics & Monitoring System ===\n");

        MetricsManager metricsManager = new MetricsManager();
        ApplicationMetrics appMetrics = new ApplicationMetrics(metricsManager);
        HealthCheckRegistry healthRegistry = new HealthCheckRegistry();
        SystemMonitor systemMonitor = new SystemMonitor(metricsManager);

        // Example 1: Counter metrics
        System.out.println("--- Example 1: Counters ---");
        Counter visitCounter = metricsManager.getCounter("page.visits");

        visitCounter.inc();    // Increment by 1
        visitCounter.inc(5);   // Increment by 5

        System.out.println("Page visits: " + visitCounter.getCount());

        // Example 2: Meter metrics (rate)
        System.out.println("\n--- Example 2: Meters (Rate Tracking) ---");
        Meter requestMeter = metricsManager.getMeter("requests");

        for (int i = 0; i < 100; i++) {
            requestMeter.mark();
            Thread.sleep(10);
        }

        System.out.println("Total requests: " + requestMeter.getCount());
        System.out.println("Mean rate: " + requestMeter.getMeanRate() + " req/sec");
        System.out.println("1-minute rate: " + requestMeter.getOneMinuteRate() + " req/sec");

        // Example 3: Histogram metrics (distribution)
        System.out.println("\n--- Example 3: Histograms (Distribution) ---");
        Histogram responseSizes = metricsManager.getHistogram("response.sizes");

        Random random = new Random();
        for (int i = 0; i < 1000; i++) {
            responseSizes.update(random.nextInt(10000) + 100);
        }

        Snapshot snapshot = responseSizes.getSnapshot();
        System.out.println("Response size statistics:");
        System.out.println("  Count: " + responseSizes.getCount());
        System.out.println("  Min: " + snapshot.getMin() + " bytes");
        System.out.println("  Max: " + snapshot.getMax() + " bytes");
        System.out.println("  Mean: " + snapshot.getMean() + " bytes");
        System.out.println("  Median: " + snapshot.getMedian() + " bytes");
        System.out.println("  95th percentile: " + snapshot.get95thPercentile() + " bytes");
        System.out.println("  99th percentile: " + snapshot.get99thPercentile() + " bytes");

        // Example 4: Timer metrics (latency)
        System.out.println("\n--- Example 4: Timers (Latency Tracking) ---");
        Timer responseTimer = metricsManager.getTimer("response.time");

        // Simulate API calls with varying latency
        for (int i = 0; i < 100; i++) {
            Timer.Context context = responseTimer.time();
            try {
                Thread.sleep(random.nextInt(100) + 10);
            } finally {
                context.stop();
            }
        }

        Snapshot timerSnapshot = responseTimer.getSnapshot();
        System.out.println("Response time statistics:");
        System.out.println("  Count: " + responseTimer.getCount());
        System.out.println("  Mean: " + timerSnapshot.getMean() / 1_000_000 + " ms");
        System.out.println("  Median: " + timerSnapshot.getMedian() / 1_000_000 + " ms");
        System.out.println("  95th percentile: " + timerSnapshot.get95thPercentile() / 1_000_000 + " ms");
        System.out.println("  99th percentile: " + timerSnapshot.get99thPercentile() / 1_000_000 + " ms");

        // Example 5: Application metrics
        System.out.println("\n--- Example 5: Application Metrics ---");

        // Simulate requests
        for (int i = 0; i < 50; i++) {
            boolean success = random.nextDouble() > 0.1; // 90% success rate
            long responseSize = random.nextInt(5000) + 500;
            long duration = random.nextInt(200) + 50;

            appMetrics.recordRequest(success, responseSize, duration);

            // Simulate database queries
            appMetrics.recordDatabaseQuery(random.nextInt(100) + 10);
        }

        System.out.println("Application metrics recorded");

        // Example 6: Health checks
        System.out.println("\n--- Example 6: Health Checks ---");

        healthRegistry.register(new HealthCheck("database", () -> {
            // Simulate database health check
            return random.nextDouble() > 0.1; // 90% healthy
        }));

        healthRegistry.register(new HealthCheck("cache", () -> {
            // Simulate cache health check
            return true;
        }));

        healthRegistry.register(new HealthCheck("external-api", () -> {
            // Simulate external API health check
            return random.nextDouble() > 0.2; // 80% healthy
        }));

        Map<String, HealthCheckResult> healthResults = healthRegistry.runAllChecks();
        System.out.println("Health check results:");
        healthResults.values().forEach(result ->
            System.out.println("  " + result)
        );

        System.out.println("Overall health: " + (healthRegistry.isHealthy() ? "HEALTHY" : "UNHEALTHY"));

        // Example 7: System monitoring
        System.out.println("\n--- Example 7: System Metrics ---");
        Runtime runtime = Runtime.getRuntime();
        System.out.println("Memory usage:");
        System.out.println("  Used: " + (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024) + " MB");
        System.out.println("  Free: " + runtime.freeMemory() / (1024 * 1024) + " MB");
        System.out.println("  Max: " + runtime.maxMemory() / (1024 * 1024) + " MB");
        System.out.println("Active threads: " + Thread.activeCount());

        // Example 8: Metrics snapshot
        System.out.println("\n--- Example 8: Metrics Snapshot ---");
        Map<String, Object> metricsSnapshot = metricsManager.getMetricsSnapshot();
        System.out.println("Total metrics tracked: " + metricsSnapshot.size());
        System.out.println("\nSample metrics:");
        metricsSnapshot.entrySet().stream()
            .limit(5)
            .forEach(entry -> System.out.println("  " + entry.getKey() + ": " + entry.getValue()));

        // Cleanup
        systemMonitor.shutdown();
        metricsManager.shutdown();

        System.out.println("\n=== Metrics & Monitoring Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Counters for event counting");
        System.out.println("  ✓ Meters for rate tracking");
        System.out.println("  ✓ Histograms for distribution analysis");
        System.out.println("  ✓ Timers for latency measurement");
        System.out.println("  ✓ JVM metrics (memory, GC, threads)");
        System.out.println("  ✓ Health checks");
        System.out.println("  ✓ Percentile calculations");
        System.out.println("  ✓ Real-time monitoring");
    }
}
