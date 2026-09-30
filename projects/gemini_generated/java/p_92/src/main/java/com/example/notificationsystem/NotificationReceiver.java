package com.example.notificationsystem;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class NotificationReceiver {

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void receiveNotification(Notification notification) {
        System.out.println("Received notification: " + notification);
        // Process the notification (e.g., send email, push notification, etc.)
        // Acknowledgment is automatic by default in Spring AMQP for successful processing
    }
}
