package com.example.kafka.service;

import com.example.kafka.model.Notification;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class NotificationListener {

    @KafkaListener(topics = "#{'${app.kafka.topic}'}", containerFactory = "kafkaListenerContainerFactory")
    public void listen(Notification notification) {
        System.out.println("Consumed notification: " + notification);
    }
}
