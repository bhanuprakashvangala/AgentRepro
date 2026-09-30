package com.example.notification.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class NotificationPayload {

    @NotBlank(message = "Recipient is required")
    private String recipient;

    @NotBlank(message = "Subject is required")
    @Size(max = 120, message = "Subject must be at most 120 characters")
    private String subject;

    @NotBlank(message = "Body is required")
    private String body;

    public NotificationPayload() {
    }

    public NotificationPayload(String recipient, String subject, String body) {
        this.recipient = recipient;
        this.subject = subject;
        this.body = body;
    }

    public String getRecipient() {
        return recipient;
    }

    public void setRecipient(String recipient) {
        this.recipient = recipient;
    }

    public String getSubject() {
        return subject;
    }

    public void setSubject(String subject) {
        this.subject = subject;
    }

    public String getBody() {
        return body;
    }

    public void setBody(String body) {
        this.body = body;
    }

    @Override
    public String toString() {
        return "NotificationPayload{" +
                "recipient='" + recipient + '\'' +
                ", subject='" + subject + '\'' +
                ", bodyLength=" + (body == null ? 0 : body.length()) +
                '}';
    }
}
