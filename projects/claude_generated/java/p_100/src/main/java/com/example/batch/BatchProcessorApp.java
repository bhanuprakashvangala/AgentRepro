package com.example.batch;

import com.google.gson.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

enum JobStatus {
    PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
}

interface Job {
    String getId();
    String getName();
    void execute() throws Exception;
    int getPriority(); // Higher value = higher priority
}

class JobResult {
    private final String jobId;
    private final JobStatus status;
    private final Instant startTime;
    private final Instant endTime;
    private final String errorMessage;
    private final Object result;

    public JobResult(String jobId, JobStatus status, Instant startTime,
                    Instant endTime, Object result, String errorMessage) {
        this.jobId = jobId;
        this.status = status;
        this.startTime = startTime;
        this.endTime = endTime;
        this.result = result;
        this.errorMessage = errorMessage;
    }

    public long getDurationMs() {
        return Duration.between(startTime, endTime).toMillis();
    }

    public String getJobId() { return jobId; }
    public JobStatus getStatus() { return status; }
    public Instant getStartTime() { return startTime; }
    public Instant getEndTime() { return endTime; }
    public String getErrorMessage() { return errorMessage; }
    public Object getResult() { return result; }

    @Override
    public String toString() {
        return String.format("JobResult{id=%s, status=%s, duration=%dms}",
            jobId, status, getDurationMs());
    }
}

interface JobProgressListener {
    void onJobStart(String jobId);
    void onJobProgress(String jobId, int progress);
    void onJobComplete(String jobId, JobResult result);
}

class BatchJob implements Job {
    private final String id;
    private final String name;
    private final Runnable task;
    private final int priority;

    public BatchJob(String name, Runnable task) {
        this(name, task, 0);
    }

    public BatchJob(String name, Runnable task, int priority) {
        this.id = UUID.randomUUID().toString();
        this.name = name;
        this.task = task;
        this.priority = priority;
    }

    @Override
    public String getId() { return id; }

    @Override
    public String getName() { return name; }

    @Override
    public void execute() {
        task.run();
    }

    @Override
    public int getPriority() { return priority; }
}

class JobQueue {
    private final PriorityBlockingQueue<Job> queue;
    private final Map<String, JobStatus> jobStatuses = new ConcurrentHashMap<>();

    public JobQueue() {
        this.queue = new PriorityBlockingQueue<>(100,
            Comparator.comparingInt(Job::getPriority).reversed());
    }

    public void submit(Job job) {
        queue.offer(job);
        jobStatuses.put(job.getId(), JobStatus.PENDING);
        System.out.println("Job submitted: " + job.getName() + " (Priority: " + job.getPriority() + ")");
    }

    public Job take() throws InterruptedException {
        return queue.take();
    }

    public boolean isEmpty() {
        return queue.isEmpty();
    }

    public int size() {
        return queue.size();
    }

    public void updateStatus(String jobId, JobStatus status) {
        jobStatuses.put(jobId, status);
    }

    public JobStatus getStatus(String jobId) {
        return jobStatuses.getOrDefault(jobId, JobStatus.PENDING);
    }

    public Map<JobStatus, Long> getStatusCounts() {
        return jobStatuses.values().stream()
            .collect(Collectors.groupingBy(s -> s, Collectors.counting()));
    }
}

class BatchProcessor {
    private final JobQueue jobQueue;
    private final ExecutorService executorService;
    private final List<JobResult> results = new CopyOnWriteArrayList<>();
    private final List<JobProgressListener> listeners = new CopyOnWriteArrayList<>();
    private final AtomicInteger activeJobs = new AtomicInteger(0);

    public BatchProcessor(int threadPoolSize) {
        this.jobQueue = new JobQueue();
        this.executorService = Executors.newFixedThreadPool(threadPoolSize);
    }

    public void addProgressListener(JobProgressListener listener) {
        listeners.add(listener);
    }

    public void submitJob(Job job) {
        jobQueue.submit(job);
    }

    public void submitJobs(List<Job> jobs) {
        jobs.forEach(this::submitJob);
    }

    public void processAll() {
        System.out.println("\nStarting batch processing...");

        while (!jobQueue.isEmpty() || activeJobs.get() > 0) {
            try {
                if (!jobQueue.isEmpty()) {
                    Job job = jobQueue.take();
                    activeJobs.incrementAndGet();

                    executorService.submit(() -> {
                        processJob(job);
                        activeJobs.decrementAndGet();
                    });
                } else {
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        executorService.shutdown();
        try {
            executorService.awaitTermination(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("\nBatch processing complete!");
        printStatistics();
    }

    private void processJob(Job job) {
        String jobId = job.getId();
        Instant startTime = Instant.now();

        notifyStart(jobId);
        jobQueue.updateStatus(jobId, JobStatus.RUNNING);

        try {
            System.out.println("Executing: " + job.getName() + " [Thread: " +
                Thread.currentThread().getName() + "]");

            job.execute();

            Instant endTime = Instant.now();
            JobResult result = new JobResult(jobId, JobStatus.COMPLETED,
                startTime, endTime, null, null);
            results.add(result);
            jobQueue.updateStatus(jobId, JobStatus.COMPLETED);

            notifyComplete(jobId, result);

        } catch (Exception e) {
            Instant endTime = Instant.now();
            JobResult result = new JobResult(jobId, JobStatus.FAILED,
                startTime, endTime, null, e.getMessage());
            results.add(result);
            jobQueue.updateStatus(jobId, JobStatus.FAILED);

            System.err.println("Job failed: " + job.getName() + " - " + e.getMessage());
            notifyComplete(jobId, result);
        }
    }

    private void notifyStart(String jobId) {
        listeners.forEach(listener -> listener.onJobStart(jobId));
    }

    private void notifyComplete(String jobId, JobResult result) {
        listeners.forEach(listener -> listener.onJobComplete(jobId, result));
    }

    public List<JobResult> getResults() {
        return new ArrayList<>(results);
    }

    public void printStatistics() {
        System.out.println("\n=== Batch Processing Statistics ===");
        System.out.println("Total jobs: " + results.size());

        long completed = results.stream()
            .filter(r -> r.getStatus() == JobStatus.COMPLETED)
            .count();
        long failed = results.stream()
            .filter(r -> r.getStatus() == JobStatus.FAILED)
            .count();

        System.out.println("Completed: " + completed);
        System.out.println("Failed: " + failed);

        if (!results.isEmpty()) {
            double avgDuration = results.stream()
                .mapToLong(JobResult::getDurationMs)
                .average()
                .orElse(0);
            long totalDuration = results.stream()
                .mapToLong(JobResult::getDurationMs)
                .sum();

            System.out.println("Average job duration: " + avgDuration + "ms");
            System.out.println("Total processing time: " + totalDuration + "ms");
        }
    }
}

// ETL Job Example
class ETLJob implements Job {
    private final String id;
    private final String name;
    private final List<Map<String, Object>> data;
    private final int priority;

    public ETLJob(String name, List<Map<String, Object>> data, int priority) {
        this.id = UUID.randomUUID().toString();
        this.name = name;
        this.data = data;
        this.priority = priority;
    }

    @Override
    public String getId() { return id; }

    @Override
    public String getName() { return name; }

    @Override
    public int getPriority() { return priority; }

    @Override
    public void execute() throws Exception {
        // Extract
        System.out.println("  [" + name + "] Extracting " + data.size() + " records...");
        Thread.sleep(100);

        // Transform
        System.out.println("  [" + name + "] Transforming data...");
        for (Map<String, Object> record : data) {
            // Simulate transformation
            record.put("processed", true);
            record.put("timestamp", System.currentTimeMillis());
        }
        Thread.sleep(150);

        // Load
        System.out.println("  [" + name + "] Loading " + data.size() + " records...");
        Thread.sleep(100);

        System.out.println("  [" + name + "] ETL Complete!");
    }
}

// Data Processing Job
class DataProcessingJob implements Job {
    private final String id;
    private final String name;
    private final int recordCount;

    public DataProcessingJob(String name, int recordCount) {
        this.id = UUID.randomUUID().toString();
        this.name = name;
        this.recordCount = recordCount;
    }

    @Override
    public String getId() { return id; }

    @Override
    public String getName() { return name; }

    @Override
    public int getPriority() { return 0; }

    @Override
    public void execute() throws Exception {
        System.out.println("  [" + name + "] Processing " + recordCount + " records...");

        for (int i = 0; i < recordCount; i++) {
            // Simulate processing
            if (i % (recordCount / 10) == 0) {
                System.out.println("  [" + name + "] Progress: " + (i * 100 / recordCount) + "%");
            }
            Thread.sleep(10);
        }

        System.out.println("  [" + name + "] Processing complete!");
    }
}

public class BatchProcessorApp {

    public static void main(String[] args) {
        System.out.println("=== Batch Processing & Job Scheduling System ===");
        System.out.println("This is script #100 - The final script in the collection!\n");

        // Example 1: Basic batch processing
        System.out.println("--- Example 1: Basic Batch Processing ---");

        BatchProcessor processor = new BatchProcessor(4);

        // Add progress listener
        processor.addProgressListener(new JobProgressListener() {
            @Override
            public void onJobStart(String jobId) {
                // System.out.println("Job started: " + jobId);
            }

            @Override
            public void onJobProgress(String jobId, int progress) {
                // System.out.println("Job progress: " + jobId + " - " + progress + "%");
            }

            @Override
            public void onJobComplete(String jobId, JobResult result) {
                System.out.println("  Job completed: " + result.getStatus() +
                    " (Duration: " + result.getDurationMs() + "ms)");
            }
        });

        // Submit jobs
        for (int i = 1; i <= 10; i++) {
            final int jobNum = i;
            processor.submitJob(new BatchJob("Task-" + i, () -> {
                try {
                    Thread.sleep(new Random().nextInt(500) + 200);
                    if (jobNum % 7 == 0) {
                        throw new RuntimeException("Simulated failure");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }));
        }

        processor.processAll();

        // Example 2: Priority-based scheduling
        System.out.println("\n--- Example 2: Priority-Based Job Scheduling ---");

        BatchProcessor priorityProcessor = new BatchProcessor(2);

        priorityProcessor.submitJob(new BatchJob("Low Priority Task", () -> {
            System.out.println("  Executing low priority task");
        }, 1));

        priorityProcessor.submitJob(new BatchJob("High Priority Task", () -> {
            System.out.println("  Executing HIGH priority task");
        }, 10));

        priorityProcessor.submitJob(new BatchJob("Medium Priority Task", () -> {
            System.out.println("  Executing medium priority task");
        }, 5));

        priorityProcessor.submitJob(new BatchJob("Critical Priority Task", () -> {
            System.out.println("  Executing CRITICAL priority task");
        }, 20));

        priorityProcessor.processAll();

        // Example 3: ETL Pipeline
        System.out.println("\n--- Example 3: ETL Pipeline ---");

        BatchProcessor etlProcessor = new BatchProcessor(3);

        // Create sample data
        List<Map<String, Object>> dataset1 = createSampleData(50);
        List<Map<String, Object>> dataset2 = createSampleData(75);
        List<Map<String, Object>> dataset3 = createSampleData(100);

        etlProcessor.submitJob(new ETLJob("ETL-Users", dataset1, 5));
        etlProcessor.submitJob(new ETLJob("ETL-Orders", dataset2, 3));
        etlProcessor.submitJob(new ETLJob("ETL-Products", dataset3, 1));

        etlProcessor.processAll();

        // Example 4: Data Processing Pipeline
        System.out.println("\n--- Example 4: Data Processing Pipeline ---");

        BatchProcessor dataProcessor = new BatchProcessor(4);

        dataProcessor.submitJob(new DataProcessingJob("Process-Dataset-A", 100));
        dataProcessor.submitJob(new DataProcessingJob("Process-Dataset-B", 150));
        dataProcessor.submitJob(new DataProcessingJob("Process-Dataset-C", 200));

        dataProcessor.processAll();

        // Example 5: Mixed workload with priorities
        System.out.println("\n--- Example 5: Mixed Workload ---");

        BatchProcessor mixedProcessor = new BatchProcessor(5);

        // Submit a mix of jobs
        mixedProcessor.submitJob(new BatchJob("Cleanup Task", () -> {
            System.out.println("  Performing cleanup...");
            try { Thread.sleep(200); } catch (InterruptedException e) {}
        }, 1));

        mixedProcessor.submitJob(new ETLJob("Critical ETL", createSampleData(25), 10));

        mixedProcessor.submitJob(new DataProcessingJob("Background Processing", 50));

        mixedProcessor.submitJob(new BatchJob("Report Generation", () -> {
            System.out.println("  Generating reports...");
            try { Thread.sleep(300); } catch (InterruptedException e) {}
        }, 7));

        mixedProcessor.processAll();

        System.out.println("\n╔═══════════════════════════════════════════════════════╗");
        System.out.println("║  🎉 CONGRATULATIONS! 🎉                               ║");
        System.out.println("║                                                       ║");
        System.out.println("║  You've completed all 100 scripts!                   ║");
        System.out.println("║  - 40 Python scripts (p_1 - p_40)                    ║");
        System.out.println("║  - 35 JavaScript scripts (p_41 - p_75)               ║");
        System.out.println("║  - 25 Java scripts (p_76 - p_100)                    ║");
        System.out.println("║                                                       ║");
        System.out.println("║  Total: 100 fully reproducible code samples          ║");
        System.out.println("╚═══════════════════════════════════════════════════════╝");
    }

    private static List<Map<String, Object>> createSampleData(int count) {
        List<Map<String, Object>> data = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            Map<String, Object> record = new HashMap<>();
            record.put("id", i);
            record.put("value", "data-" + i);
            data.add(record);
        }
        return data;
    }
}
