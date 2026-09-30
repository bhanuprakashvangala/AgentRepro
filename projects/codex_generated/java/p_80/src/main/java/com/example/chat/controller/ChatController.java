package com.example.chat.controller;

import com.example.chat.model.ChatMessage;
import java.util.Locale;

import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.util.StringUtils;

@Controller
public class ChatController {

    private static final String TOPIC_PREFIX = "/topic/rooms/";

    private final SimpMessagingTemplate messagingTemplate;

    public ChatController(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @MessageMapping("/chat/{roomId}/send")
    public void sendMessage(@DestinationVariable String roomId, @Payload ChatMessage message) {
        if (message == null) {
            return;
        }
        String resolvedRoom = resolveRoom(roomId);
        message.setTimestamp(System.currentTimeMillis());
        message.setRoomId(resolvedRoom);
        if (message.getType() == null) {
            message.setType(ChatMessage.MessageType.CHAT);
        }
        messagingTemplate.convertAndSend(TOPIC_PREFIX + resolvedRoom, message);
    }

    @MessageMapping("/chat/{roomId}/addUser")
    public void addUser(@DestinationVariable String roomId, @Payload ChatMessage message,
                        SimpMessageHeaderAccessor headerAccessor) {
        if (message == null || !StringUtils.hasText(message.getSender())) {
            return;
        }
        String resolvedRoom = resolveRoom(roomId);
        headerAccessor.getSessionAttributes().put("username", message.getSender());
        headerAccessor.getSessionAttributes().put("roomId", resolvedRoom);

        message.setType(ChatMessage.MessageType.JOIN);
        message.setTimestamp(System.currentTimeMillis());
        message.setRoomId(resolvedRoom);
        messagingTemplate.convertAndSend(TOPIC_PREFIX + resolvedRoom, message);
    }

    private String resolveRoom(String candidate) {
        if (!StringUtils.hasText(candidate)) {
            return "general";
        }
        String trimmed = candidate.trim();
        String normalized = trimmed.toLowerCase(Locale.ROOT).replaceAll("\\s+", "-");
        return normalized.isEmpty() ? "general" : normalized;
    }
}
