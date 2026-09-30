package com.example.ratelimiter.config;

import com.example.ratelimiter.service.RateLimiterService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class BucketRateLimiterFilter extends OncePerRequestFilter {

    private static final Logger logger = LoggerFactory.getLogger(BucketRateLimiterFilter.class);

    private final RateLimiterService rateLimiterService;

    public BucketRateLimiterFilter(RateLimiterService rateLimiterService) {
        this.rateLimiterService = rateLimiterService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String clientId = resolveClientId(request);
        if (rateLimiterService.tryConsume(clientId)) {
            filterChain.doFilter(request, response);
        } else {
            logger.warn("Rate limit exceeded for {}", clientId);
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"Too many requests\"}");
        }
    }

    private String resolveClientId(HttpServletRequest request) {
        String header = request.getHeader("X-Client-Id");
        if (header != null && !header.isBlank()) {
            return header;
        }
        return request.getRemoteAddr();
    }
}
