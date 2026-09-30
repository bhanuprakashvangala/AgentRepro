package com.example.kafka.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Notification {

    @NotBlank
    private String id;

    @NotBlank
    private String type;

    @NotBlank
    private String message;

    @NotNull
    private Long createdAt;
}
