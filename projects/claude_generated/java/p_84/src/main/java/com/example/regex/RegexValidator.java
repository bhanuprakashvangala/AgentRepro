package com.example.regex;

import java.util.*;
import java.util.regex.*;

public class RegexValidator {
    // Pre-defined patterns
    public static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,6}$"
    );

    public static final Pattern PHONE_PATTERN = Pattern.compile(
        "^\\+?[1-9]\\d{1,14}$|^\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$"
    );

    public static final Pattern URL_PATTERN = Pattern.compile(
        "^(https?://)?([\\da-z\\.-]+)\\.([a-z\\.]{2,6})([/\\w \\.-]*)*/?$",
        Pattern.CASE_INSENSITIVE
    );

    public static final Pattern IP_ADDRESS_PATTERN = Pattern.compile(
        "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    );

    public static final Pattern DATE_PATTERN = Pattern.compile(
        "^(\\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$"
    );

    public static final Pattern CREDIT_CARD_PATTERN = Pattern.compile(
        "^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$"
    );

    public static final Pattern USERNAME_PATTERN = Pattern.compile(
        "^[a-zA-Z0-9_-]{3,20}$"
    );

    public static final Pattern PASSWORD_STRONG_PATTERN = Pattern.compile(
        "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$"
    );

    private final Map<String, Pattern> customPatterns = new HashMap<>();

    public void addCustomPattern(String name, String regex) {
        customPatterns.put(name, Pattern.compile(regex));
    }

    public boolean validate(Pattern pattern, String input) {
        if (input == null) return false;
        Matcher matcher = pattern.matcher(input);
        return matcher.matches();
    }

    public boolean validateEmail(String email) {
        return validate(EMAIL_PATTERN, email);
    }

    public boolean validatePhone(String phone) {
        return validate(PHONE_PATTERN, phone);
    }

    public boolean validateURL(String url) {
        return validate(URL_PATTERN, url);
    }

    public boolean validateIPAddress(String ip) {
        return validate(IP_ADDRESS_PATTERN, ip);
    }

    public boolean validateDate(String date) {
        return validate(DATE_PATTERN, date);
    }

    public boolean validateCreditCard(String cardNumber) {
        return validate(CREDIT_CARD_PATTERN, cardNumber.replaceAll("\\s", ""));
    }

    public boolean validateUsername(String username) {
        return validate(USERNAME_PATTERN, username);
    }

    public boolean validateStrongPassword(String password) {
        return validate(PASSWORD_STRONG_PATTERN, password);
    }

    public List<String> extractMatches(Pattern pattern, String input) {
        List<String> matches = new ArrayList<>();
        Matcher matcher = pattern.matcher(input);
        while (matcher.find()) {
            matches.add(matcher.group());
        }
        return matches;
    }

    public List<String> extractEmails(String text) {
        return extractMatches(EMAIL_PATTERN, text);
    }

    public List<String> extractURLs(String text) {
        return extractMatches(URL_PATTERN, text);
    }

    public static void main(String[] args) {
        RegexValidator validator = new RegexValidator();

        // Test emails
        System.out.println("=== Email Validation ===");
        String[] emails = {"user@example.com", "invalid.email", "test@domain.co.uk"};
        for (String email : emails) {
            System.out.println(email + ": " + validator.validateEmail(email));
        }

        // Test phones
        System.out.println("\n=== Phone Validation ===");
        String[] phones = {"+1234567890", "(555) 123-4567", "123-456-7890", "invalid"};
        for (String phone : phones) {
            System.out.println(phone + ": " + validator.validatePhone(phone));
        }

        // Test URLs
        System.out.println("\n=== URL Validation ===");
        String[] urls = {"https://example.com", "http://test.org/path", "invalid-url"};
        for (String url : urls) {
            System.out.println(url + ": " + validator.validateURL(url));
        }

        // Test IP addresses
        System.out.println("\n=== IP Address Validation ===");
        String[] ips = {"192.168.1.1", "256.1.1.1", "10.0.0.1"};
        for (String ip : ips) {
            System.out.println(ip + ": " + validator.validateIPAddress(ip));
        }

        // Test dates
        System.out.println("\n=== Date Validation ===");
        String[] dates = {"2024-01-15", "2024-13-01", "2024-02-29"};
        for (String date : dates) {
            System.out.println(date + ": " + validator.validateDate(date));
        }

        // Test credit cards
        System.out.println("\n=== Credit Card Validation ===");
        String[] cards = {"4532015112830366", "5425233430109903", "1234567890123456"};
        for (String card : cards) {
            System.out.println(card + ": " + validator.validateCreditCard(card));
        }

        // Test passwords
        System.out.println("\n=== Password Validation ===");
        String[] passwords = {"Pass123!", "weak", "StrongP@ssw0rd"};
        for (String password : passwords) {
            System.out.println(password + ": " + validator.validateStrongPassword(password));
        }

        // Extract emails from text
        System.out.println("\n=== Extract Emails ===");
        String text = "Contact us at support@example.com or sales@company.org";
        List<String> extractedEmails = validator.extractEmails(text);
        System.out.println("Found emails: " + extractedEmails);

        // Extract URLs
        System.out.println("\n=== Extract URLs ===");
        String urlText = "Visit https://example.com or http://test.org for more info";
        List<String> extractedURLs = validator.extractURLs(urlText);
        System.out.println("Found URLs: " + extractedURLs);
    }
}
