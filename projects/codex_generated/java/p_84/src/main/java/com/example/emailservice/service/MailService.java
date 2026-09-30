package com.example.emailservice.service;

import com.example.emailservice.model.EmailAttachment;
import com.example.emailservice.model.EmailRequest;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.Locale;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;

@Service
public class MailService {

    private static final Logger logger = LoggerFactory.getLogger(MailService.class);

    private final JavaMailSender mailSender;
    private final SpringTemplateEngine templateEngine;

    public MailService(JavaMailSender mailSender, SpringTemplateEngine templateEngine) {
        this.mailSender = mailSender;
        this.templateEngine = templateEngine;
    }

    public void sendEmail(EmailRequest request) throws MessagingException {
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true, StandardCharsets.UTF_8.name());

        helper.setSubject(request.getSubject());
        helper.setTo(request.getTo().toArray(String[]::new));
        if (request.getCc() != null && !request.getCc().isEmpty()) {
            helper.setCc(request.getCc().toArray(String[]::new));
        }
        if (request.getBcc() != null && !request.getBcc().isEmpty()) {
            helper.setBcc(request.getBcc().toArray(String[]::new));
        }

        Context context = new Context(Locale.getDefault());
        request.getVariables().forEach(context::setVariable);

        String htmlBody = templateEngine.process(request.getTemplate(), context);
        helper.setText(htmlBody, true);

        List<EmailAttachment> attachments = request.getAttachments();
        if (attachments != null) {
            for (EmailAttachment attachment : attachments) {
                byte[] data = Base64.getDecoder().decode(attachment.getBase64Data());
                helper.addAttachment(attachment.getFileName(),
                        () -> new ByteArrayInputStream(data),
                        attachment.getContentType());
            }
        }

        mailSender.send(message);
        logger.info("Email queued to {} (subject: {})", request.getTo(), request.getSubject());
    }
}
