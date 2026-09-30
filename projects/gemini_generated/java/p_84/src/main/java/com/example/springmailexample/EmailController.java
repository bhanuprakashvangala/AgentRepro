package com.example.springmailexample;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.thymeleaf.context.Context;

import javax.mail.MessagingException;

@RestController
public class EmailController {

    @Autowired
    private EmailService emailService;

    @PostMapping("/send-email")
    public String sendEmail(@RequestParam String to, @RequestParam String subject, @RequestParam String name) {
        Context context = new Context();
        context.setVariable("name", name);

        try {
            // Create a dummy file for attachment
            File dummyFile = new File("attachment.txt");
            dummyFile.createNewFile();

            emailService.sendEmailWithAttachment(to, subject, "email-template", context, "attachment.txt");
            return "Email sent successfully!";
        } catch (MessagingException | java.io.IOException e) {
            e.printStackTrace();
            return "Error sending email: " + e.getMessage();
        }
    }
}