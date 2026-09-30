package com.example.notification.controller;

import com.example.notification.model.NotificationPayload;
import com.example.notification.service.NotificationPublisher;
import jakarta.validation.Valid;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/notifications")
public class NotificationController {

    private final NotificationPublisher publisher;

    public NotificationController(NotificationPublisher publisher) {
        this.publisher = publisher;
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> publish(@RequestBody @Valid NotificationPayload payload) {
        publisher.send(payload);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(Map.of(
                "status", "queued",
                "recipient", payload.getRecipient()
        ));
    }
}
