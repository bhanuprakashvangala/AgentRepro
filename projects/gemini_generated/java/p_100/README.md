# Password Encryption Service with BCrypt

This project demonstrates a password encryption service using Spring Boot and BCrypt (via Spring Security).

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd password-encryption
   ```

2. **Build the project:**
   ```bash
   mvn clean install
   ```

3. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start on port 8080.

## Usage

### Hash a Password

Send a POST request to `http://localhost:8080/hash` with the password as a request parameter.

**Example using cURL:**

```bash
curl -X POST "http://localhost:8080/hash?password=mysecretpassword"
```

This will return the BCrypt hashed password.

### Verify a Password

Send a POST request to `http://localhost:8080/verify` with the raw password and the encoded password as request parameters.

**Example using cURL:**

First, hash a password:

```bash
HASHED_PASSWORD=$(curl -X POST "http://localhost:8080/hash?password=mysecretpassword")
echo "Hashed password: $HASHED_PASSWORD"
```

Then, use the hashed password to verify:

```bash
curl -X POST "http://localhost:8080/verify?rawPassword=mysecretpassword&encodedPassword=$HASHED_PASSWORD"
```

**Successful Response:**

```
Password matches!
```

**Incorrect Password Response:**

```bash
curl -X POST "http://localhost:8080/verify?rawPassword=wrongpassword&encodedPassword=$HASHED_PASSWORD"
```

```
Password does not match.
```

## Configuring Hash Strength

The BCrypt hash strength can be configured in `src/main/resources/application.properties` using the `bcrypt.strength` property. A higher value means more secure hashing but takes longer to compute.
