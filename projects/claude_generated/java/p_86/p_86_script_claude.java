package com.example.scheduler;

import jakarta.persistence.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.scheduling.TaskScheduler;
import org.springframework.scheduling.annotation.*;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.scheduling.support.CronTrigger;
import org.springframework.stereotype.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;

@Entity
@Table(name = "task_execution_log")
class TaskExecutionLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String taskName;
    private LocalDateTime executionTime;
    private Long executionDurationMs;
    private String status;
    private String errorMessage;

    public TaskExecutionLog() {}

    public TaskExecutionLog(String taskName, LocalDateTime executionTime,
                           Long executionDurationMs, String status) {
        this.taskName = taskName;
        this.executionTime = executionTime;
        this.executionDurationMs = executionDurationMs;
        this.status = status;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTaskName() { return taskName; }
    public void setTaskName(String taskName) { this.taskName = taskName; }
    public LocalDateTime getExecutionTime() { return executionTime; }
    public void setExecutionTime(LocalDateTime executionTime) { this.executionTime = executionTime; }
    public Long getExecutionDurationMs() { return executionDurationMs; }
    public void setExecutionDurationMs(Long executionDurationMs) { this.executionDurationMs = executionDurationMs; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
}

interface TaskExecutionLogRepository extends JpaRepository<TaskExecutionLog, Long> {
    List<TaskExecutionLog> findByTaskNameOrderByExecutionTimeDesc(String taskName);
    List<TaskExecutionLog> findByExecutionTimeBefore(LocalDateTime dateTime);
}

@Service
class TaskLogger {
    private final TaskExecutionLogRepository repository;

    public TaskLogger(TaskExecutionLogRepository repository) {
        this.repository = repository;
    }

    public void logExecution(String taskName, Runnable task) {
        LocalDateTime startTime = LocalDateTime.now();
        long start = System.currentTimeMillis();
        TaskExecutionLog log = new TaskExecutionLog();
        log.setTaskName(taskName);
        log.setExecutionTime(startTime);

        try {
            task.run();
            long duration = System.currentTimeMillis() - start;
            log.setExecutionDurationMs(duration);
            log.setStatus("SUCCESS");
        } catch (Exception e) {
            long duration = System.currentTimeMillis() - start;
            log.setExecutionDurationMs(duration);
            log.setStatus("FAILED");
            log.setErrorMessage(e.getMessage());
            throw e;
        } finally {
            repository.save(log);
        }
    }

    public List<TaskExecutionLog> getTaskHistory(String taskName) {
        return repository.findByTaskNameOrderByExecutionTimeDesc(taskName);
    }

    public void cleanupOldLogs(int daysToKeep) {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(daysToKeep);
        List<TaskExecutionLog> oldLogs = repository.findByExecutionTimeBefore(cutoffDate);
        repository.deleteAll(oldLogs);
        System.out.println("Cleaned up " + oldLogs.size() + " old task logs");
    }
}

@Service
class ScheduledTaskService {
    private final TaskLogger taskLogger;
    private int taskCounter = 0;

    public ScheduledTaskService(TaskLogger taskLogger) {
        this.taskLogger = taskLogger;
    }

    // Fixed rate - runs every 10 seconds
    @Scheduled(fixedRate = 10000)
    public void fixedRateTask() {
        taskLogger.logExecution("FixedRateTask", () -> {
            taskCounter++;
            System.out.println("[" + LocalDateTime.now() + "] Fixed Rate Task executed. Count: " + taskCounter);
        });
    }

    // Fixed delay - waits 5 seconds after previous execution completes
    @Scheduled(fixedDelay = 5000)
    public void fixedDelayTask() {
        taskLogger.logExecution("FixedDelayTask", () -> {
            System.out.println("[" + LocalDateTime.now() + "] Fixed Delay Task started");
            try {
                Thread.sleep(2000); // Simulate work
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            System.out.println("[" + LocalDateTime.now() + "] Fixed Delay Task completed");
        });
    }

    // Cron expression - runs every minute at :00 seconds
    @Scheduled(cron = "0 * * * * *")
    public void cronTask() {
        taskLogger.logExecution("CronTask", () -> {
            System.out.println("[" + LocalDateTime.now() + "] Cron Task - runs every minute");
        });
    }

    // Daily report at 9 AM
    @Scheduled(cron = "0 0 9 * * *")
    public void dailyReport() {
        taskLogger.logExecution("DailyReport", () -> {
            System.out.println("[" + LocalDateTime.now() + "] Generating daily report...");
            // Simulate report generation
            int recordsProcessed = new Random().nextInt(1000) + 100;
            System.out.println("Daily report complete. Records processed: " + recordsProcessed);
        });
    }

    // Weekly cleanup on Sunday at midnight
    @Scheduled(cron = "0 0 0 * * SUN")
    public void weeklyCleanup() {
        taskLogger.logExecution("WeeklyCleanup", () -> {
            System.out.println("[" + LocalDateTime.now() + "] Running weekly cleanup...");
            taskLogger.cleanupOldLogs(30); // Keep last 30 days
            System.out.println("Weekly cleanup complete");
        });
    }

    // Health check every 30 seconds
    @Scheduled(fixedRate = 30000, initialDelay = 5000)
    public void healthCheck() {
        taskLogger.logExecution("HealthCheck", () -> {
            boolean healthy = checkSystemHealth();
            if (healthy) {
                System.out.println("[" + LocalDateTime.now() + "] Health check: HEALTHY");
            } else {
                System.out.println("[" + LocalDateTime.now() + "] Health check: UNHEALTHY");
            }
        });
    }

    private boolean checkSystemHealth() {
        // Simulate health check logic
        return Math.random() > 0.1; // 90% healthy
    }

    public void printTaskStatistics() {
        System.out.println("\n=== Task Execution Statistics ===");
        String[] taskNames = {"FixedRateTask", "FixedDelayTask", "CronTask", "HealthCheck"};

        for (String taskName : taskNames) {
            List<TaskExecutionLog> history = taskLogger.getTaskHistory(taskName);
            if (!history.isEmpty()) {
                long avgDuration = (long) history.stream()
                    .mapToLong(TaskExecutionLog::getExecutionDurationMs)
                    .average()
                    .orElse(0);

                long successCount = history.stream()
                    .filter(log -> "SUCCESS".equals(log.getStatus()))
                    .count();

                System.out.printf("%s: %d executions, %.1f%% success rate, avg duration: %d ms%n",
                    taskName, history.size(),
                    (successCount * 100.0 / history.size()), avgDuration);
            }
        }
    }
}

@Service
class DynamicTaskScheduler {
    private final TaskScheduler taskScheduler;
    private final Map<String, ScheduledFuture<?>> scheduledTasks = new ConcurrentHashMap<>();
    private final TaskLogger taskLogger;

    public DynamicTaskScheduler(TaskScheduler taskScheduler, TaskLogger taskLogger) {
        this.taskScheduler = taskScheduler;
        this.taskLogger = taskLogger;
    }

    public void scheduleTask(String taskId, Runnable task, String cronExpression) {
        ScheduledFuture<?> scheduledTask = taskScheduler.schedule(
            () -> taskLogger.logExecution(taskId, task),
            new CronTrigger(cronExpression)
        );
        scheduledTasks.put(taskId, scheduledTask);
        System.out.println("Scheduled task: " + taskId + " with cron: " + cronExpression);
    }

    public void scheduleFixedRateTask(String taskId, Runnable task, long periodMs) {
        ScheduledFuture<?> scheduledTask = taskScheduler.scheduleAtFixedRate(
            () -> taskLogger.logExecution(taskId, task),
            Duration.ofMillis(periodMs)
        );
        scheduledTasks.put(taskId, scheduledTask);
        System.out.println("Scheduled fixed-rate task: " + taskId + " every " + periodMs + "ms");
    }

    public void cancelTask(String taskId) {
        ScheduledFuture<?> scheduledTask = scheduledTasks.get(taskId);
        if (scheduledTask != null) {
            scheduledTask.cancel(false);
            scheduledTasks.remove(taskId);
            System.out.println("Cancelled task: " + taskId);
        }
    }

    public boolean isTaskScheduled(String taskId) {
        ScheduledFuture<?> task = scheduledTasks.get(taskId);
        return task != null && !task.isCancelled() && !task.isDone();
    }

    public Set<String> getScheduledTaskIds() {
        return new HashSet<>(scheduledTasks.keySet());
    }
}

@SpringBootApplication
@EnableScheduling
public class TaskSchedulerApp {

    @Bean
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(10);
        scheduler.setThreadNamePrefix("scheduled-task-");
        scheduler.setAwaitTerminationSeconds(60);
        scheduler.setWaitForTasksToCompleteOnShutdown(true);
        scheduler.initialize();
        return scheduler;
    }

    public static void main(String[] args) throws InterruptedException {
        var context = SpringApplication.run(TaskSchedulerApp.class, args);

        System.out.println("=== Task Scheduler Application Started ===");
        System.out.println("Scheduled tasks are running in the background...\n");

        // Get services
        ScheduledTaskService scheduledTaskService = context.getBean(ScheduledTaskService.class);
        DynamicTaskScheduler dynamicScheduler = context.getBean(DynamicTaskScheduler.class);

        // Let scheduled tasks run for a bit
        System.out.println("Letting scheduled tasks run for 30 seconds...");
        Thread.sleep(30000);

        // Show statistics
        scheduledTaskService.printTaskStatistics();

        // Demonstrate dynamic task scheduling
        System.out.println("\n=== Dynamic Task Scheduling ===");

        // Schedule a dynamic task
        dynamicScheduler.scheduleFixedRateTask("DynamicTask1",
            () -> System.out.println("[Dynamic] Task 1 executed at " + LocalDateTime.now()),
            3000);

        // Schedule task with cron
        dynamicScheduler.scheduleTask("DynamicTask2",
            () -> System.out.println("[Dynamic] Task 2 executed at " + LocalDateTime.now()),
            "*/5 * * * * *"); // Every 5 seconds

        System.out.println("Running dynamic tasks for 20 seconds...");
        Thread.sleep(20000);

        // Check scheduled tasks
        System.out.println("\nCurrently scheduled dynamic tasks: " +
            dynamicScheduler.getScheduledTaskIds());

        // Cancel one task
        dynamicScheduler.cancelTask("DynamicTask1");
        System.out.println("After cancellation: " + dynamicScheduler.getScheduledTaskIds());

        System.out.println("\n=== Task Scheduler Demo Complete ===");
        System.out.println("Application will continue running scheduled tasks...");
        System.out.println("Press Ctrl+C to stop.");
    }
}
