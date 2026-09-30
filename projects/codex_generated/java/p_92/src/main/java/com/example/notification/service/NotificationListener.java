package com.example.notification.service;

import com.example.notification.config.RabbitConfig;
import com.example.notification.model.NotificationPayload;
import com.rabbitmq.client.Channel;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class NotificationListener {

    private static final Logger logger = LoggerFactory.getLogger(NotificationListener.class);

    @RabbitListener(queues = RabbitConfig.QUEUE_NAME, containerFactory = "rabbitListenerContainerFactory")
    public void onMessage(NotificationPayload payload, Message message, Channel channel) throws IOException {
        long deliveryTag = message.getMessageProperties().getDeliveryTag();
        try {
            logger.info("Received notification: {}", payload);
            // Simulate processing. Insert real processing logic here.
            processNotification(payload);
            channel.basicAck(deliveryTag, false);
        } catch (Exception ex) {
            logger.error("Failed to process notification", ex);
            channel.basicNack(deliveryTag, false, false);
        }
    }

    private void processNotification(NotificationPayload payload) {
        // In a real system, send email/push/etc.
        logger.info("Processed notification for {}", payload.getRecipient());
    }
}
