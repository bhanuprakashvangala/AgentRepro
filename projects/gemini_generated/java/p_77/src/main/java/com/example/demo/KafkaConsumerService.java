package com.example.demo;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class KafkaConsumerService {

    @KafkaListener(topics = "my_topic", groupId = "my_group_id")
    public void consume(String message) {
        System.out.println(String.format("#### -> Consumed message -> %s", message));
    }
}
