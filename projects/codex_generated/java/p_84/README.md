# Spring Email Service

HTML email delivery service built with Spring Boot, JavaMail, and Thymeleaf templates. Supports rich HTML rendering, dynamic template variables, and binary attachments provided via base64.

## Features
- Uses `spring-boot-starter-mail` with JavaMail for SMTP delivery
- Thymeleaf templates (`src/main/resources/templates/email/notification.html`) for dynamic, styled emails
- REST endpoint `POST /api/email/send` for triggering emails
- Optional CC/BCC recipients and per-request attachments (base64 encoded)

## Prerequisites
- Java 17 or newer
- Apache Maven 3.9+ (for building/running)
- SMTP server credentials (for local development you can use [MailHog](https://github.com/mailhog/MailHog))

## Configure SMTP
Update `src/main/resources/application.properties` with your SMTP settings. Example for MailHog (default in the repo):
```properties
spring.mail.host=localhost
spring.mail.port=1025
spring.mail.username=
spring.mail.password=
spring.mail.properties.mail.smtp.auth=false
spring.mail.properties.mail.smtp.starttls.enable=false
```
For production SMTP providers, supply the correct host, port, username/password, and enable TLS as required.

## Build & Run
```bash
cd 1-GPT/p_84
mvn clean package
mvn spring-boot:run
```

The application starts on `http://localhost:8080`.

## Send an Email
Create a JSON payload similar to the following (with base64 data for attachments):
```json
{
  "to": ["recipient@example.com"],
  "subject": "Welcome to Spring Email Service",
  "template": "email/notification",
  "variables": {
    "preheader": "You're all set!",
    "title": "Hello, Recipient",
    "message": "<p>Thanks for trying our <strong>email service</strong>.</p>",
    "ctaUrl": "https://example.com",
    "ctaText": "Open dashboard"
  },
  "attachments": [
    {
      "fileName": "hello.txt",
      "contentType": "text/plain",
      "base64Data": "SGVsbG8sIGVtYWlsIQ=="
    }
  ]
}
```
Send it:
```bash
curl -X POST http://localhost:8080/api/email/send \
  -H "Content-Type: application/json" \
  -d @payload.json
```
The endpoint returns `202 Accepted` when the message is queued successfully.

## Template Customization
- Add more Thymeleaf templates under `src/main/resources/templates/email/`
- Reference them via the `template` field (without `.html`)
- Pass variables through the `variables` map; they are available in the template context

## Testing with MailHog
1. Start MailHog (`MailHog` binary or Docker image)
2. Run the Spring application
3. Perform the `curl` request above
4. Open `http://localhost:8025` to view the captured email

## Stop
Press `Ctrl+C` in the terminal running `spring-boot:run`.
