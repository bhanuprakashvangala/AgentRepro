package com.example.validation.constraint;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import java.lang.annotation.Documented;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;

import static java.lang.annotation.ElementType.FIELD;
import static java.lang.annotation.ElementType.PARAMETER;
import static java.lang.annotation.RetentionPolicy.RUNTIME;

/**
 * Rejects email addresses from known disposable domains.
 */
@Target({FIELD, PARAMETER})
@Retention(RUNTIME)
@Constraint(validatedBy = NoDisposableEmailValidator.class)
@Documented
public @interface NoDisposableEmail {

    String message() default "Disposable email addresses are not allowed";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};

    /**
     * Domains considered disposable. Defaults include common providers.
     */
    String[] blacklist() default {
            "mailinator.com",
            "10minutemail.com",
            "guerrillamail.com",
            "tempmail.com"
    };
}
