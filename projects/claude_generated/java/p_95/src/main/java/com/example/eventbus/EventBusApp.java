package com.example.eventbus;

import com.google.gson.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Predicate;
import java.util.regex.Pattern;

class Event<T> {
    private final String id;
    private final String topic;
    private final T payload;
    private final Instant timestamp;
    private final Map<String, String> metadata;
    private final int priority;

    public Event(String topic, T payload) {
        this(topic, payload, 0);
    }

    public Event(String topic, T payload, int priority) {
        this.id = UUID.randomUUID().toString();
        this.topic = topic;
        this.payload = payload;
        this.timestamp = Instant.now();
        this.metadata = new HashMap<>();
        this.priority = priority;
    }

    public String getId() { return id; }
    public String getTopic() { return topic; }
    public T getPayload() { return payload; }
    public Instant getTimestamp() { return timestamp; }
    public Map<String, String> getMetadata() { return metadata; }
    public int getPriority() { return priority; }

    public void addMetadata(String key, String value) {
        metadata.put(key, value);
    }

    @Override
    public String toString() {
        return String.format("Event{id=%s, topic=%s, payload=%s, priority=%d, timestamp=%s}",
            id, topic, payload, priority, timestamp);
    }
}

interface EventSubscriber<T> {
    void onEvent(Event<T> event);
    default void onError(Event<T> event, Throwable error) {
        System.err.println("Error handling event: " + event.getId() + " - " + error.getMessage());
    }
}

class Subscription<T> {
    private final String subscriberId;
    private final String topicPattern;
    private final EventSubscriber<T> subscriber;
    private final Pattern compiledPattern;
    private final Predicate<Event<T>> filter;
    private boolean active;

    public Subscription(String subscriberId, String topicPattern,
                       EventSubscriber<T> subscriber, Predicate<Event<T>> filter) {
        this.subscriberId = subscriberId;
        this.topicPattern = topicPattern;
        this.subscriber = subscriber;
        this.compiledPattern = Pattern.compile(topicPattern.replace("*", ".*"));
        this.filter = filter;
        this.active = true;
    }

    public boolean matches(String topic) {
        return compiledPattern.matcher(topic).matches();
    }

    public boolean shouldHandle(Event<?> event) {
        return active && matches(event.getTopic()) &&
               (filter == null || filter.test(event));
    }

    public void handle(Event<T> event) {
        try {
            subscriber.onEvent(event);
        } catch (Exception e) {
            subscriber.onError(event, e);
        }
    }

    public String getSubscriberId() { return subscriberId; }
    public String getTopicPattern() { return topicPattern; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
}

class EventBus {
    private final Map<String, List<Subscription<?>>> subscriptions = new ConcurrentHashMap<>();
    private final ExecutorService asyncExecutor;
    private final List<Event<?>> eventHistory = new CopyOnWriteArrayList<>();
    private final int maxHistorySize = 1000;
    private final Queue<Event<?>> deadLetterQueue = new ConcurrentLinkedQueue<>();

    public EventBus() {
        this.asyncExecutor = Executors.newFixedThreadPool(4);
    }

    public EventBus(int asyncThreads) {
        this.asyncExecutor = Executors.newFixedThreadPool(asyncThreads);
    }

    public <T> String subscribe(String topic, EventSubscriber<T> subscriber) {
        return subscribe(topic, subscriber, null);
    }

    public <T> String subscribe(String topic, EventSubscriber<T> subscriber,
                               Predicate<Event<T>> filter) {
        String subscriberId = UUID.randomUUID().toString();
        Subscription<T> subscription = new Subscription<>(subscriberId, topic, subscriber, filter);

        subscriptions.computeIfAbsent(topic, k -> new CopyOnWriteArrayList<>())
                    .add(subscription);

        System.out.println("Subscribed: " + subscriberId + " to topic: " + topic);
        return subscriberId;
    }

    public void unsubscribe(String subscriberId) {
        subscriptions.values().forEach(subs ->
            subs.removeIf(sub -> sub.getSubscriberId().equals(subscriberId))
        );
        System.out.println("Unsubscribed: " + subscriberId);
    }

    public <T> void publish(Event<T> event) {
        publishSync(event);
    }

    @SuppressWarnings("unchecked")
    public <T> void publishSync(Event<T> event) {
        addToHistory(event);

        List<Subscription<?>> matchingSubscriptions = findMatchingSubscriptions(event.getTopic());

        // Sort by priority (higher priority first)
        List<Subscription<?>> sortedSubs = new ArrayList<>(matchingSubscriptions);
        sortedSubs.sort((a, b) -> Integer.compare(b.getSubscriberId().hashCode(),
                                                  a.getSubscriberId().hashCode()));

        for (Subscription<?> subscription : sortedSubs) {
            if (subscription.shouldHandle(event)) {
                try {
                    ((Subscription<T>) subscription).handle(event);
                } catch (Exception e) {
                    System.err.println("Subscriber error: " + e.getMessage());
                    deadLetterQueue.offer(event);
                }
            }
        }
    }

    @SuppressWarnings("unchecked")
    public <T> void publishAsync(Event<T> event) {
        addToHistory(event);

        List<Subscription<?>> matchingSubscriptions = findMatchingSubscriptions(event.getTopic());

        for (Subscription<?> subscription : matchingSubscriptions) {
            if (subscription.shouldHandle(event)) {
                asyncExecutor.submit(() -> {
                    try {
                        ((Subscription<T>) subscription).handle(event);
                    } catch (Exception e) {
                        System.err.println("Async subscriber error: " + e.getMessage());
                        deadLetterQueue.offer(event);
                    }
                });
            }
        }
    }

    private List<Subscription<?>> findMatchingSubscriptions(String topic) {
        List<Subscription<?>> matching = new ArrayList<>();

        subscriptions.forEach((pattern, subs) -> {
            for (Subscription<?> sub : subs) {
                if (sub.matches(topic)) {
                    matching.add(sub);
                }
            }
        });

        return matching;
    }

    private <T> void addToHistory(Event<T> event) {
        eventHistory.add(event);
        if (eventHistory.size() > maxHistorySize) {
            eventHistory.remove(0);
        }
    }

    public List<Event<?>> getEventHistory() {
        return new ArrayList<>(eventHistory);
    }

    public List<Event<?>> getEventHistory(String topic) {
        return eventHistory.stream()
            .filter(e -> e.getTopic().equals(topic))
            .toList();
    }

    @SuppressWarnings("unchecked")
    public <T> void replay(String topic, EventSubscriber<T> subscriber) {
        getEventHistory(topic).forEach(event -> {
            try {
                subscriber.onEvent((Event<T>) event);
            } catch (Exception e) {
                System.err.println("Replay error: " + e.getMessage());
            }
        });
    }

    public Queue<Event<?>> getDeadLetterQueue() {
        return new ConcurrentLinkedQueue<>(deadLetterQueue);
    }

    public int getSubscriberCount() {
        return subscriptions.values().stream()
            .mapToInt(List::size)
            .sum();
    }

    public int getSubscriberCount(String topic) {
        return (int) subscriptions.getOrDefault(topic, Collections.emptyList()).stream()
            .filter(Subscription::isActive)
            .count();
    }

    public void shutdown() {
        asyncExecutor.shutdown();
        try {
            asyncExecutor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            asyncExecutor.shutdownNow();
        }
    }

    public void clearHistory() {
        eventHistory.clear();
    }

    public Map<String, Integer> getTopicStats() {
        Map<String, Integer> stats = new HashMap<>();
        subscriptions.forEach((topic, subs) ->
            stats.put(topic, subs.size())
        );
        return stats;
    }
}

// Sample Event Payloads
record UserEvent(String userId, String action) {}
record OrderEvent(String orderId, double amount, String status) {}
record SystemEvent(String service, String level, String message) {}

public class EventBusApp {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Event Bus / Pub-Sub System ===\n");

        EventBus eventBus = new EventBus();

        // Example 1: Basic pub-sub
        System.out.println("--- Example 1: Basic Publish-Subscribe ---");

        String sub1 = eventBus.subscribe("user.login", new EventSubscriber<UserEvent>() {
            @Override
            public void onEvent(Event<UserEvent> event) {
                System.out.println("  [Subscriber 1] User logged in: " + event.getPayload().userId());
            }
        });

        String sub2 = eventBus.subscribe("user.login", new EventSubscriber<UserEvent>() {
            @Override
            public void onEvent(Event<UserEvent> event) {
                System.out.println("  [Subscriber 2] Logging user activity: " + event.getPayload());
            }
        });

        Event<UserEvent> loginEvent = new Event<>("user.login",
            new UserEvent("user123", "login"));
        eventBus.publish(loginEvent);

        // Example 2: Topic patterns with wildcards
        System.out.println("\n--- Example 2: Topic Patterns (Wildcards) ---");

        eventBus.subscribe("user.*", new EventSubscriber<UserEvent>() {
            @Override
            public void onEvent(Event<UserEvent> event) {
                System.out.println("  [Wildcard Subscriber] Captured: " + event.getTopic() +
                    " - " + event.getPayload());
            }
        });

        eventBus.publish(new Event<>("user.login", new UserEvent("alice", "login")));
        eventBus.publish(new Event<>("user.logout", new UserEvent("bob", "logout")));
        eventBus.publish(new Event<>("user.update", new UserEvent("charlie", "update")));

        // Example 3: Event filtering
        System.out.println("\n--- Example 3: Event Filtering ---");

        eventBus.subscribe("order.created",
            new EventSubscriber<OrderEvent>() {
                @Override
                public void onEvent(Event<OrderEvent> event) {
                    System.out.println("  [High-Value Filter] Processing high-value order: " +
                        event.getPayload());
                }
            },
            event -> event.getPayload().amount() >= 100.0 // Only orders >= $100
        );

        eventBus.publish(new Event<>("order.created",
            new OrderEvent("order1", 50.0, "pending")));
        eventBus.publish(new Event<>("order.created",
            new OrderEvent("order2", 150.0, "pending")));
        eventBus.publish(new Event<>("order.created",
            new OrderEvent("order3", 200.0, "pending")));

        // Example 4: Asynchronous publishing
        System.out.println("\n--- Example 4: Asynchronous Publishing ---");

        eventBus.subscribe("system.alert", new EventSubscriber<SystemEvent>() {
            @Override
            public void onEvent(Event<SystemEvent> event) {
                System.out.println("  [Async Handler] " + Thread.currentThread().getName() +
                    " - Processing: " + event.getPayload().message());
                try {
                    Thread.sleep(100); // Simulate work
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });

        for (int i = 0; i < 5; i++) {
            eventBus.publishAsync(new Event<>("system.alert",
                new SystemEvent("api", "INFO", "Request " + (i + 1))));
        }

        Thread.sleep(1000); // Wait for async processing

        // Example 5: Event history and replay
        System.out.println("\n--- Example 5: Event History & Replay ---");

        eventBus.publish(new Event<>("data.sync", "Sync event 1"));
        eventBus.publish(new Event<>("data.sync", "Sync event 2"));
        eventBus.publish(new Event<>("data.sync", "Sync event 3"));

        System.out.println("Total events in history: " + eventBus.getEventHistory().size());
        System.out.println("Events for 'data.sync': " + eventBus.getEventHistory("data.sync").size());

        System.out.println("\nReplaying 'data.sync' events:");
        eventBus.replay("data.sync", new EventSubscriber<String>() {
            @Override
            public void onEvent(Event<String> event) {
                System.out.println("  [Replay] " + event.getPayload());
            }
        });

        // Example 6: Error handling and dead letter queue
        System.out.println("\n--- Example 6: Error Handling & Dead Letter Queue ---");

        eventBus.subscribe("error.test", new EventSubscriber<String>() {
            @Override
            public void onEvent(Event<String> event) {
                throw new RuntimeException("Simulated error");
            }
        });

        eventBus.publish(new Event<>("error.test", "This will fail"));
        eventBus.publish(new Event<>("error.test", "This will also fail"));

        System.out.println("Dead letter queue size: " + eventBus.getDeadLetterQueue().size());

        // Example 7: Subscriber management
        System.out.println("\n--- Example 7: Subscriber Management ---");

        System.out.println("Total subscribers: " + eventBus.getSubscriberCount());
        System.out.println("Subscribers for 'user.login': " +
            eventBus.getSubscriberCount("user.login"));

        System.out.println("\nUnsubscribing: " + sub1);
        eventBus.unsubscribe(sub1);

        System.out.println("Subscribers for 'user.login' after unsubscribe: " +
            eventBus.getSubscriberCount("user.login"));

        // Example 8: Topic statistics
        System.out.println("\n--- Example 8: Topic Statistics ---");

        Map<String, Integer> topicStats = eventBus.getTopicStats();
        System.out.println("Topic subscription counts:");
        topicStats.forEach((topic, count) ->
            System.out.println("  " + topic + ": " + count + " subscriber(s)")
        );

        // Example 9: Event metadata
        System.out.println("\n--- Example 9: Event Metadata ---");

        Event<String> metadataEvent = new Event<>("notification.send", "Test message");
        metadataEvent.addMetadata("priority", "high");
        metadataEvent.addMetadata("source", "api");
        metadataEvent.addMetadata("userId", "user456");

        eventBus.subscribe("notification.send", new EventSubscriber<String>() {
            @Override
            public void onEvent(Event<String> event) {
                System.out.println("  [Metadata Handler] Message: " + event.getPayload());
                System.out.println("  Metadata: " + event.getMetadata());
            }
        });

        eventBus.publish(metadataEvent);

        // Cleanup
        eventBus.shutdown();

        System.out.println("\n=== Event Bus Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Topic-based pub-sub");
        System.out.println("  ✓ Wildcard topic patterns");
        System.out.println("  ✓ Event filtering");
        System.out.println("  ✓ Synchronous and asynchronous dispatch");
        System.out.println("  ✓ Event history and replay");
        System.out.println("  ✓ Dead letter queue");
        System.out.println("  ✓ Subscriber lifecycle management");
        System.out.println("  ✓ Event metadata");
    }
}
