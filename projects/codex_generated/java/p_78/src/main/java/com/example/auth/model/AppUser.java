package com.example.auth.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.Set;

@Data
@AllArgsConstructor
public class AppUser {
    private String username;
    private String password;
    private Set<String> roles;
}
