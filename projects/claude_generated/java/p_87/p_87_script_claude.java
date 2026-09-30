package com.example.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.*;
import org.springframework.http.*;
import org.springframework.security.authentication.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.stereotype.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

// JWT Token Provider
@Component
class JwtTokenProvider {
    private final SecretKey secretKey;
    private final long validityInMilliseconds = 3600000; // 1 hour
    private final long refreshValidityInMilliseconds = 86400000; // 24 hours

    public JwtTokenProvider() {
        this.secretKey = Keys.secretKeyFor(SignatureAlgorithm.HS256);
    }

    public String createToken(String username, Collection<? extends GrantedAuthority> roles) {
        Claims claims = Jwts.claims().setSubject(username);
        claims.put("roles", roles.stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.toList()));

        Date now = new Date();
        Date validity = new Date(now.getTime() + validityInMilliseconds);

        return Jwts.builder()
            .setClaims(claims)
            .setIssuedAt(now)
            .setExpiration(validity)
            .signWith(secretKey)
            .compact();
    }

    public String createRefreshToken(String username) {
        Date now = new Date();
        Date validity = new Date(now.getTime() + refreshValidityInMilliseconds);

        return Jwts.builder()
            .setSubject(username)
            .setIssuedAt(now)
            .setExpiration(validity)
            .signWith(secretKey)
            .compact();
    }

    public String getUsername(String token) {
        return Jwts.parserBuilder()
            .setSigningKey(secretKey)
            .build()
            .parseClaimsJws(token)
            .getBody()
            .getSubject();
    }

    @SuppressWarnings("unchecked")
    public List<String> getRoles(String token) {
        Claims claims = Jwts.parserBuilder()
            .setSigningKey(secretKey)
            .build()
            .parseClaimsJws(token)
            .getBody();

        return (List<String>) claims.get("roles");
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                .setSigningKey(secretKey)
                .build()
                .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}

// JWT Authentication Filter
class JwtAuthenticationFilter extends OncePerRequestFilter {
    private final JwtTokenProvider tokenProvider;

    public JwtAuthenticationFilter(JwtTokenProvider tokenProvider) {
        this.tokenProvider = tokenProvider;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {
        String token = resolveToken(request);

        if (token != null && tokenProvider.validateToken(token)) {
            String username = tokenProvider.getUsername(token);
            List<String> roles = tokenProvider.getRoles(token);

            List<GrantedAuthority> authorities = roles.stream()
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());

            UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(username, null, authorities);

            SecurityContextHolder.getContext().setAuthentication(auth);
        }

        filterChain.doFilter(request, response);
    }

    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}

// User Model
class User {
    private String username;
    private String password;
    private String email;
    private Set<String> roles;

    public User(String username, String password, String email, Set<String> roles) {
        this.username = username;
        this.password = password;
        this.email = email;
        this.roles = roles;
    }

    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public String getEmail() { return email; }
    public Set<String> getRoles() { return roles; }
    public void setPassword(String password) { this.password = password; }
}

// User Service
@Service
class UserService implements UserDetailsService {
    private final Map<String, User> users = new HashMap<>();
    private final PasswordEncoder passwordEncoder;

    public UserService(PasswordEncoder passwordEncoder) {
        this.passwordEncoder = passwordEncoder;

        // Initialize with demo users
        createUser("admin", "admin123", "admin@example.com",
            Set.of("ROLE_ADMIN", "ROLE_USER"));
        createUser("user", "user123", "user@example.com",
            Set.of("ROLE_USER"));
    }

    public User createUser(String username, String password, String email, Set<String> roles) {
        String encodedPassword = passwordEncoder.encode(password);
        User user = new User(username, encodedPassword, email, roles);
        users.put(username, user);
        return user;
    }

    public Optional<User> findByUsername(String username) {
        return Optional.ofNullable(users.get(username));
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = users.get(username);
        if (user == null) {
            throw new UsernameNotFoundException("User not found: " + username);
        }

        List<GrantedAuthority> authorities = user.getRoles().stream()
            .map(SimpleGrantedAuthority::new)
            .collect(Collectors.toList());

        return new org.springframework.security.core.userdetails.User(
            user.getUsername(),
            user.getPassword(),
            authorities
        );
    }

    public boolean authenticate(String username, String password) {
        Optional<User> userOpt = findByUsername(username);
        return userOpt.isPresent() &&
               passwordEncoder.matches(password, userOpt.get().getPassword());
    }
}

// Authentication Request/Response DTOs
record LoginRequest(String username, String password) {}
record RegisterRequest(String username, String password, String email) {}
record AuthResponse(String accessToken, String refreshToken, String username, Set<String> roles) {}
record RefreshTokenRequest(String refreshToken) {}

// Authentication Controller
@RestController
@RequestMapping("/api/auth")
class AuthController {
    private final UserService userService;
    private final JwtTokenProvider tokenProvider;

    public AuthController(UserService userService, JwtTokenProvider tokenProvider) {
        this.userService = userService;
        this.tokenProvider = tokenProvider;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest request) {
        if (userService.findByUsername(request.username()).isPresent()) {
            return ResponseEntity.badRequest()
                .body(Map.of("error", "Username already exists"));
        }

        User user = userService.createUser(
            request.username(),
            request.password(),
            request.email(),
            Set.of("ROLE_USER")
        );

        return ResponseEntity.ok(Map.of(
            "message", "User registered successfully",
            "username", user.getUsername()
        ));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        if (!userService.authenticate(request.username(), request.password())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", "Invalid credentials"));
        }

        User user = userService.findByUsername(request.username()).orElseThrow();
        List<GrantedAuthority> authorities = user.getRoles().stream()
            .map(SimpleGrantedAuthority::new)
            .collect(Collectors.toList());

        String accessToken = tokenProvider.createToken(request.username(), authorities);
        String refreshToken = tokenProvider.createRefreshToken(request.username());

        return ResponseEntity.ok(new AuthResponse(
            accessToken,
            refreshToken,
            user.getUsername(),
            user.getRoles()
        ));
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refreshToken(@RequestBody RefreshTokenRequest request) {
        String refreshToken = request.refreshToken();

        if (!tokenProvider.validateToken(refreshToken)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", "Invalid refresh token"));
        }

        String username = tokenProvider.getUsername(refreshToken);
        User user = userService.findByUsername(username).orElseThrow();

        List<GrantedAuthority> authorities = user.getRoles().stream()
            .map(SimpleGrantedAuthority::new)
            .collect(Collectors.toList());

        String newAccessToken = tokenProvider.createToken(username, authorities);

        return ResponseEntity.ok(Map.of(
            "accessToken", newAccessToken,
            "username", username
        ));
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        User user = userService.findByUsername(auth.getName()).orElseThrow();
        return ResponseEntity.ok(Map.of(
            "username", user.getUsername(),
            "email", user.getEmail(),
            "roles", user.getRoles()
        ));
    }
}

// Protected Resources Controller
@RestController
@RequestMapping("/api")
class ResourceController {

    @GetMapping("/public")
    public ResponseEntity<?> publicEndpoint() {
        return ResponseEntity.ok(Map.of(
            "message", "This is a public endpoint",
            "timestamp", new Date()
        ));
    }

    @GetMapping("/user")
    public ResponseEntity<?> userEndpoint() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return ResponseEntity.ok(Map.of(
            "message", "Hello " + auth.getName(),
            "access", "USER level access",
            "authorities", auth.getAuthorities()
        ));
    }

    @GetMapping("/admin")
    public ResponseEntity<?> adminEndpoint() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return ResponseEntity.ok(Map.of(
            "message", "Hello Admin " + auth.getName(),
            "access", "ADMIN level access",
            "authorities", auth.getAuthorities()
        ));
    }
}

// Security Configuration
@Configuration
@EnableWebSecurity
class SecurityConfig {

    private final JwtTokenProvider tokenProvider;

    public SecurityConfig(JwtTokenProvider tokenProvider) {
        this.tokenProvider = tokenProvider;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/api/public").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/user/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(new JwtAuthenticationFilter(tokenProvider),
                           UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

@SpringBootApplication
public class JwtSecurityApp {

    public static void main(String[] args) {
        SpringApplication.run(JwtSecurityApp.class, args);

        System.out.println("\n=== JWT Security Application Started ===");
        System.out.println("\nAvailable Endpoints:");
        System.out.println("  POST /api/auth/register - Register new user");
        System.out.println("  POST /api/auth/login    - Login and get JWT token");
        System.out.println("  POST /api/auth/refresh  - Refresh access token");
        System.out.println("  GET  /api/auth/me       - Get current user (requires auth)");
        System.out.println("  GET  /api/public        - Public endpoint");
        System.out.println("  GET  /api/user          - User endpoint (requires USER role)");
        System.out.println("  GET  /api/admin         - Admin endpoint (requires ADMIN role)");

        System.out.println("\nDemo Users:");
        System.out.println("  Username: admin, Password: admin123 (ROLE_ADMIN, ROLE_USER)");
        System.out.println("  Username: user, Password: user123 (ROLE_USER)");

        System.out.println("\nExample Usage:");
        System.out.println("  1. Login: curl -X POST http://localhost:8080/api/auth/login \\");
        System.out.println("       -H \"Content-Type: application/json\" \\");
        System.out.println("       -d '{\"username\":\"admin\",\"password\":\"admin123\"}'");
        System.out.println("\n  2. Access protected endpoint:");
        System.out.println("     curl http://localhost:8080/api/user \\");
        System.out.println("       -H \"Authorization: Bearer YOUR_TOKEN\"");
    }
}
