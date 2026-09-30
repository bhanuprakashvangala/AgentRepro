package com.example.validation.constraint;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import java.util.Arrays;
import java.util.Locale;
import java.util.Set;
import java.util.stream.Collectors;

public class NoDisposableEmailValidator implements ConstraintValidator<NoDisposableEmail, String> {

    private Set<String> blacklist;

    @Override
    public void initialize(NoDisposableEmail constraintAnnotation) {
        blacklist = Arrays.stream(constraintAnnotation.blacklist())
                .map(domain -> domain.toLowerCase(Locale.ROOT))
                .collect(Collectors.toSet());
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null || value.isBlank()) {
            return true; // handled by other annotations such as @NotBlank
        }
        int atIndex = value.lastIndexOf('@');
        if (atIndex < 0 || atIndex == value.length() - 1) {
            return true; // malformed email handled by @Email; do not double-report
        }
        String domain = value.substring(atIndex + 1).toLowerCase(Locale.ROOT);
        if (blacklist.contains(domain)) {
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate(
                            "Email domain '" + domain + "' is not permitted")
                    .addConstraintViolation();
            return false;
        }
        return true;
    }
}
