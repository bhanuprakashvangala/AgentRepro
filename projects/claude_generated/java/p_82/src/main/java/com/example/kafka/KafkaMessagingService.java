package com.example.kafka;

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;

public class KafkaMessagingService {
    private static final Logger logger = LoggerFactory.getLogger(KafkaMessagingService.class);

    static class KafkaProducerService {
        private final Producer<String, String> producer;
        private final String bootstrapServers;

        public KafkaProducerService(String bootstrapServers) {
            this.bootstrapServers = bootstrapServers;
            Properties props = new Properties();
            props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
            props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
            props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
            props.put(ProducerConfig.ACKS_CONFIG, "all");
            props.put(ProducerConfig.RETRIES_CONFIG, 3);
            props.put(ProducerConfig.LINGER_MS_CONFIG, 1);
            this.producer = new KafkaProducer<>(props);
            logger.info("Kafka Producer initialized: {}", bootstrapServers);
        }

        public void sendMessage(String topic, String key, String value) {
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
            producer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    logger.error("Error sending message", exception);
                } else {
                    logger.info("Message sent: topic={}, partition={}, offset={}",
                            metadata.topic(), metadata.partition(), metadata.offset());
                }
            });
        }

        public void sendMessageSync(String topic, String key, String value) throws Exception {
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);
            RecordMetadata metadata = producer.send(record).get();
            logger.info("Message sent synchronously: topic={}, partition={}, offset={}",
                    metadata.topic(), metadata.partition(), metadata.offset());
        }

        public void close() {
            if (producer != null) {
                producer.flush();
                producer.close();
                logger.info("Kafka Producer closed");
            }
        }
    }

    static class KafkaConsumerService {
        private final Consumer<String, String> consumer;
        private final String bootstrapServers;
        private volatile boolean running = false;

        public KafkaConsumerService(String bootstrapServers, String groupId) {
            this.bootstrapServers = bootstrapServers;
            Properties props = new Properties();
            props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
            props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
            props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
            props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
            props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
            props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
            props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, "1000");
            this.consumer = new KafkaConsumer<>(props);
            logger.info("Kafka Consumer initialized: {}, groupId={}", bootstrapServers, groupId);
        }

        public void subscribe(String... topics) {
            consumer.subscribe(Arrays.asList(topics));
            logger.info("Subscribed to topics: {}", Arrays.toString(topics));
        }

        public void startConsuming(MessageHandler handler) {
            running = true;
            logger.info("Starting consumer...");

            while (running) {
                try {
                    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                    for (ConsumerRecord<String, String> record : records) {
                        logger.info("Consumed: topic={}, partition={}, offset={}, key={}, value={}",
                                record.topic(), record.partition(), record.offset(),
                                record.key(), record.value());
                        handler.handle(record.key(), record.value());
                    }
                } catch (Exception e) {
                    logger.error("Error consuming messages", e);
                }
            }
        }

        public void stop() {
            running = false;
            logger.info("Stopping consumer...");
        }

        public void close() {
            if (consumer != null) {
                consumer.close();
                logger.info("Kafka Consumer closed");
            }
        }

        @FunctionalInterface
        public interface MessageHandler {
            void handle(String key, String value);
        }
    }

    public static void main(String[] args) throws Exception {
        String bootstrapServers = "localhost:9092";
        String topic = "test-topic";

        // Start producer
        KafkaProducerService producer = new KafkaProducerService(bootstrapServers);

        // Send messages
        System.out.println("\n=== Sending Messages ===");
        for (int i = 1; i <= 5; i++) {
            String key = "key-" + i;
            String value = "Message " + i + ": Hello Kafka!";
            producer.sendMessage(topic, key, value);
            Thread.sleep(100);
        }

        // Start consumer in separate thread
        KafkaConsumerService consumer = new KafkaConsumerService(bootstrapServers, "test-group");
        consumer.subscribe(topic);

        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(() -> {
            consumer.startConsuming((key, value) -> {
                System.out.println("Processed message: " + key + " = " + value);
            });
        });

        // Let consumer run for a while
        System.out.println("\n=== Consuming Messages ===");
        Thread.sleep(5000);

        // Cleanup
        consumer.stop();
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
        consumer.close();
        producer.close();

        System.out.println("\n=== Demo Complete ===");
    }
}
