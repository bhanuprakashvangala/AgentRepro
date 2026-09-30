# STOMP WebSocket Chat

Real-time chat application built with Spring Boot, Spring WebSocket, and STOMP. Users can join named chat rooms, exchange messages, and receive join/leave notifications.

## Features
- STOMP-over-WebSocket endpoint with SockJS fallback (`/ws`)
- Multiple chat rooms (`/topic/rooms/{roomId}`) with automatic room name normalization
- Join/leave announcements and timestamped chat messages
- Simple HTML client served from `src/main/resources/static/index.html`
- Graceful handling of disconnect events to broadcast leave notices

## Prerequisites
- Java Development Kit (JDK) 17 or later
- Apache Maven 3.9+ available on `PATH`

> **Note:** If Maven is not installed, download it from https://maven.apache.org/download.cgi and add `mvn` to your environment path before proceeding.

## Install & Run
1. Navigate to the project:
   ```bash
   cd 1-GPT/p_80
   ```
2. (Optional) Package the application:
   ```bash
   mvn clean package
   ```
3. Start the server:
   ```bash
   mvn spring-boot:run
   ```
4. Open the client in a browser: http://localhost:8080/index.html

## Using the Chat Client
1. Enter a username and room name. Room names are normalized to lower-case with hyphens (e.g., `General Chat` → `general-chat`).
2. Click **Connect** to join the room. A join message appears for all participants.
3. Send messages via the input field. The server broadcasts them to subscribers of that room only.
4. Click **Disconnect** to leave. A leave notification is broadcast automatically.

You can open multiple browser tabs (or different browsers) to simulate concurrent users. Each tab can connect to different rooms simultaneously by disconnecting and reconnecting.

## Build Artifacts
After running `mvn clean package`, the runnable JAR is generated at:
```
target/stomp-chat-1.0.0.jar
```
You can run it directly with:
```bash
java -jar target/stomp-chat-1.0.0.jar
```

## Troubleshooting
- **`mvn: command not found`** – Install Maven and ensure `mvn` is available on your `PATH`.
- **Port conflicts** – Change `server.port` in `src/main/resources/application.properties`.
- **WebSocket blocked by CORS** – The sample allows any origin. For production, adjust the allowed origins in `WebSocketConfig`.
