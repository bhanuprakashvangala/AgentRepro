package com.example.notificationsystem;

import java.io.Serializable;

public class Notification implements Serializable {
    private String recipient;
    private String message;

    public Notification() {
    }

    public Notification(String recipient, String message) {
        this.recipient = recipient;
        this.message = message;
    }

    public String getRecipient() {
        return recipient;
    }

    public void setRecipient(String recipient) {
        this.recipient = recipient;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Override
    public String toString() {
        return "Notification{" +
               "recipient='" + recipient + "'" +
               ", message='" + message + "'" +
               '}';
    }
}
