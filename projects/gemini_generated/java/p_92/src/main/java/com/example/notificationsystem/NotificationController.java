package com.example.notificationsystem;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class NotificationController {

    private final NotificationSender notificationSender;

    @Autowired
    public NotificationController(NotificationSender notificationSender) {
        this.notificationSender = notificationSender;
    }

    @PostMapping("/send-notification")
    public String sendNotification(@RequestBody Notification notification) {
        notificationSender.sendNotification(notification);
        return "Notification sent successfully!";
    }
}
