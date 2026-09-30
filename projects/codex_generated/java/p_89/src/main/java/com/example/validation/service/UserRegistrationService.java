package com.example.validation.service;

import com.example.validation.model.UserRegistrationRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class UserRegistrationService {

    private static final Logger logger = LoggerFactory.getLogger(UserRegistrationService.class);

    public String register(UserRegistrationRequest request) {
        String id = UUID.randomUUID().toString();
        logger.info("Registering user {} {} with roles {}", request.getFirstName(),
                request.getLastName(), request.getRoles());
        return id;
    }
}
