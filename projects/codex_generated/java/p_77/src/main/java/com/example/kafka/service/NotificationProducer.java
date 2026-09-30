package com.example.kafka.service;

import com.example.kafka.model.Notification;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class NotificationProducer {

    private final KafkaTemplate<String, Notification> kafkaTemplate;
    private final String topic;

    public NotificationProducer(KafkaTemplate<String, Notification> kafkaTemplate,
                                @Value("${app.kafka.topic}") String topic) {
        this.kafkaTemplate = kafkaTemplate;
        this.topic = topic;
    }

    public void send(Notification notification) {
        kafkaTemplate.send(topic, notification.getId(), notification).whenComplete((result, ex) -> {
            if (ex != null) {
                System.err.println("Failed to send message: " + ex.getMessage());
            } else {
                System.out.println("Message sent to partition " + result.getRecordMetadata().partition());
            }
        });
    }
}
