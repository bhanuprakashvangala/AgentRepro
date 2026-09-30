package com.example.email;

import freemarker.template.*;
import jakarta.mail.*;
import jakarta.mail.internet.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

class EmailConfig {
    private String host;
    private int port;
    private String username;
    private String password;
    private boolean enableTLS;
    private boolean enableSSL;

    public EmailConfig(String host, int port, String username, String password) {
        this.host = host;
        this.port = port;
        this.username = username;
        this.password = password;
        this.enableTLS = true;
        this.enableSSL = false;
    }

    public Session createSession() {
        Properties props = new Properties();
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.host", host);
        props.put("mail.smtp.port", port);
        props.put("mail.smtp.starttls.enable", enableTLS);
        props.put("mail.smtp.ssl.enable", enableSSL);

        return Session.getInstance(props, new Authenticator() {
            @Override
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication(username, password);
            }
        });
    }

    public void setEnableTLS(boolean enableTLS) { this.enableTLS = enableTLS; }
    public void setEnableSSL(boolean enableSSL) { this.enableSSL = enableSSL; }
}

class EmailMessage {
    private String from;
    private List<String> to = new ArrayList<>();
    private List<String> cc = new ArrayList<>();
    private List<String> bcc = new ArrayList<>();
    private String subject;
    private String textBody;
    private String htmlBody;
    private Map<String, File> attachments = new HashMap<>();
    private Map<String, String> inlineImages = new HashMap<>();

    public EmailMessage from(String from) {
        this.from = from;
        return this;
    }

    public EmailMessage to(String... recipients) {
        to.addAll(Arrays.asList(recipients));
        return this;
    }

    public EmailMessage cc(String... recipients) {
        cc.addAll(Arrays.asList(recipients));
        return this;
    }

    public EmailMessage bcc(String... recipients) {
        bcc.addAll(Arrays.asList(recipients));
        return this;
    }

    public EmailMessage subject(String subject) {
        this.subject = subject;
        return this;
    }

    public EmailMessage text(String text) {
        this.textBody = text;
        return this;
    }

    public EmailMessage html(String html) {
        this.htmlBody = html;
        return this;
    }

    public EmailMessage attach(String filename, File file) {
        attachments.put(filename, file);
        return this;
    }

    public EmailMessage inline(String contentId, String imagePath) {
        inlineImages.put(contentId, imagePath);
        return this;
    }

    public String getFrom() { return from; }
    public List<String> getTo() { return to; }
    public List<String> getCc() { return cc; }
    public List<String> getBcc() { return bcc; }
    public String getSubject() { return subject; }
    public String getTextBody() { return textBody; }
    public String getHtmlBody() { return htmlBody; }
    public Map<String, File> getAttachments() { return attachments; }
    public Map<String, String> getInlineImages() { return inlineImages; }
}

class TemplateEngine {
    private Configuration config;

    public TemplateEngine() {
        config = new Configuration(Configuration.VERSION_2_3_32);
        config.setDefaultEncoding("UTF-8");
        config.setTemplateExceptionHandler(TemplateExceptionHandler.RETHROW_HANDLER);
    }

    public void setTemplateDirectory(File directory) throws IOException {
        config.setDirectoryForTemplateLoading(directory);
    }

    public String renderTemplate(String templateName, Map<String, Object> data)
            throws IOException, TemplateException {
        Template template = config.getTemplate(templateName);
        StringWriter writer = new StringWriter();
        template.process(data, writer);
        return writer.toString();
    }
}

public class EmailService {
    private EmailConfig emailConfig;
    private Session session;
    private TemplateEngine templateEngine;

    public EmailService(EmailConfig config) {
        this.emailConfig = config;
        this.session = config.createSession();
        this.templateEngine = new TemplateEngine();
    }

    public void setTemplateDirectory(String directory) throws IOException {
        templateEngine.setTemplateDirectory(new File(directory));
    }

    public void sendEmail(EmailMessage message) throws MessagingException, IOException {
        MimeMessage mimeMessage = new MimeMessage(session);

        // Set from
        mimeMessage.setFrom(new InternetAddress(message.getFrom()));

        // Set recipients
        for (String to : message.getTo()) {
            mimeMessage.addRecipient(Message.RecipientType.TO, new InternetAddress(to));
        }
        for (String cc : message.getCc()) {
            mimeMessage.addRecipient(Message.RecipientType.CC, new InternetAddress(cc));
        }
        for (String bcc : message.getBcc()) {
            mimeMessage.addRecipient(Message.RecipientType.BCC, new InternetAddress(bcc));
        }

        // Set subject
        mimeMessage.setSubject(message.getSubject());

        // Build message body
        if (message.getAttachments().isEmpty() && message.getInlineImages().isEmpty()) {
            // Simple message
            if (message.getHtmlBody() != null) {
                mimeMessage.setContent(message.getHtmlBody(), "text/html; charset=utf-8");
            } else {
                mimeMessage.setText(message.getTextBody());
            }
        } else {
            // Multipart message with attachments
            Multipart multipart = new MimeMultipart();

            // Add text/html body
            MimeBodyPart bodyPart = new MimeBodyPart();
            if (message.getHtmlBody() != null) {
                bodyPart.setContent(message.getHtmlBody(), "text/html; charset=utf-8");
            } else {
                bodyPart.setText(message.getTextBody());
            }
            multipart.addBodyPart(bodyPart);

            // Add inline images
            for (Map.Entry<String, String> entry : message.getInlineImages().entrySet()) {
                MimeBodyPart imagePart = new MimeBodyPart();
                imagePart.attachFile(entry.getValue());
                imagePart.setContentID("<" + entry.getKey() + ">");
                imagePart.setDisposition(MimeBodyPart.INLINE);
                multipart.addBodyPart(imagePart);
            }

            // Add attachments
            for (Map.Entry<String, File> entry : message.getAttachments().entrySet()) {
                MimeBodyPart attachmentPart = new MimeBodyPart();
                attachmentPart.attachFile(entry.getValue());
                attachmentPart.setFileName(entry.getKey());
                multipart.addBodyPart(attachmentPart);
            }

            mimeMessage.setContent(multipart);
        }

        // Send the message
        Transport.send(mimeMessage);
        System.out.println("Email sent successfully to: " + message.getTo());
    }

    public void sendTemplatedEmail(String templateName, Map<String, Object> data,
                                   EmailMessage message)
            throws MessagingException, IOException, TemplateException {
        String htmlContent = templateEngine.renderTemplate(templateName, data);
        message.html(htmlContent);
        sendEmail(message);
    }

    public void sendBulkEmails(List<EmailMessage> messages) {
        int successCount = 0;
        int failureCount = 0;

        for (EmailMessage message : messages) {
            try {
                sendEmail(message);
                successCount++;
            } catch (Exception e) {
                System.err.println("Failed to send email to " + message.getTo() + ": " + e.getMessage());
                failureCount++;
            }
        }

        System.out.println("\nBulk email summary:");
        System.out.println("  Success: " + successCount);
        System.out.println("  Failures: " + failureCount);
    }

    public static void main(String[] args) {
        // Configure email service (use your SMTP settings)
        EmailConfig config = new EmailConfig(
            "smtp.gmail.com",
            587,
            "your-email@gmail.com",
            "your-app-password"
        );

        EmailService emailService = new EmailService(config);

        try {
            // Example 1: Simple text email
            System.out.println("=== Example 1: Simple Text Email ===");
            EmailMessage simpleEmail = new EmailMessage()
                .from("sender@example.com")
                .to("recipient@example.com")
                .subject("Test Email - Plain Text")
                .text("This is a simple plain text email.");

            // emailService.sendEmail(simpleEmail);
            System.out.println("Simple email prepared (uncomment to send)");

            // Example 2: HTML email
            System.out.println("\n=== Example 2: HTML Email ===");
            String htmlContent = """
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h1 style="color: #333;">Welcome to Our Service!</h1>
                    <p>Thank you for signing up. We're excited to have you on board.</p>
                    <p>Click the button below to get started:</p>
                    <a href="https://example.com" style="background-color: #4CAF50; color: white;
                       padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                       Get Started
                    </a>
                </body>
                </html>
                """;

            EmailMessage htmlEmail = new EmailMessage()
                .from("sender@example.com")
                .to("recipient@example.com")
                .subject("Welcome to Our Service")
                .html(htmlContent);

            System.out.println("HTML email prepared");

            // Example 3: Email with attachments
            System.out.println("\n=== Example 3: Email with Attachments ===");

            // Create temporary files for demonstration
            File tempFile1 = File.createTempFile("document", ".txt");
            Files.writeString(tempFile1.toPath(), "This is a sample document content.");

            File tempFile2 = File.createTempFile("report", ".txt");
            Files.writeString(tempFile2.toPath(), "This is a sample report content.");

            EmailMessage emailWithAttachments = new EmailMessage()
                .from("sender@example.com")
                .to("recipient@example.com")
                .cc("cc@example.com")
                .subject("Documents Attached")
                .text("Please find the attached documents.")
                .attach("document.txt", tempFile1)
                .attach("report.txt", tempFile2);

            System.out.println("Email with attachments prepared");
            System.out.println("  Attachments: document.txt, report.txt");

            // Example 4: Template-based email
            System.out.println("\n=== Example 4: Template-Based Email ===");

            // Create a simple template
            File templateDir = Files.createTempDirectory("email-templates").toFile();
            File templateFile = new File(templateDir, "welcome.ftl");
            String templateContent = """
                <html>
                <body>
                    <h1>Hello ${name}!</h1>
                    <p>Your account has been created successfully.</p>
                    <p>Account Details:</p>
                    <ul>
                        <li>Username: ${username}</li>
                        <li>Email: ${email}</li>
                        <li>Account Type: ${accountType}</li>
                    </ul>
                    <p>Thank you for joining us!</p>
                </body>
                </html>
                """;
            Files.writeString(templateFile.toPath(), templateContent);

            emailService.setTemplateDirectory(templateDir.getAbsolutePath());

            Map<String, Object> templateData = new HashMap<>();
            templateData.put("name", "John Doe");
            templateData.put("username", "johndoe123");
            templateData.put("email", "john@example.com");
            templateData.put("accountType", "Premium");

            EmailMessage templatedEmail = new EmailMessage()
                .from("sender@example.com")
                .to("john@example.com")
                .subject("Welcome - Your Account is Ready");

            // emailService.sendTemplatedEmail("welcome.ftl", templateData, templatedEmail);
            System.out.println("Templated email prepared with FreeMarker");

            // Example 5: Bulk email sending
            System.out.println("\n=== Example 5: Bulk Email Sending ===");
            List<EmailMessage> bulkEmails = new ArrayList<>();

            String[] recipients = {"user1@example.com", "user2@example.com", "user3@example.com"};
            for (String recipient : recipients) {
                EmailMessage bulkEmail = new EmailMessage()
                    .from("sender@example.com")
                    .to(recipient)
                    .subject("Monthly Newsletter")
                    .html("<h1>This Month's Updates</h1><p>Check out our latest features!</p>");
                bulkEmails.add(bulkEmail);
            }

            // emailService.sendBulkEmails(bulkEmails);
            System.out.println("Prepared " + bulkEmails.size() + " bulk emails");

            // Cleanup
            tempFile1.delete();
            tempFile2.delete();
            templateFile.delete();
            templateDir.delete();

            System.out.println("\n=== Email Service Examples Complete ===");
            System.out.println("Note: Uncomment sendEmail() calls and configure SMTP settings to actually send emails");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
