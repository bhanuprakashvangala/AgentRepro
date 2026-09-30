package com.example.apiversioning;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final DeprecatedApiInterceptor deprecatedApiInterceptor;

    @Autowired
    public WebConfig(DeprecatedApiInterceptor deprecatedApiInterceptor) {
        this.deprecatedApiInterceptor = deprecatedApiInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(deprecatedApiInterceptor);
    }
}
