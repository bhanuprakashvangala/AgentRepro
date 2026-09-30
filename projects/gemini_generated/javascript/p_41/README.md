# Express REST API with MongoDB

This project is a complete, self-contained REST API for user management built with Express.js. It demonstrates best practices such as input validation and global error handling.

## Features

- **Express.js Server**: A robust Node.js web server.
- **In-Memory Database**: Uses `mongodb-memory-server` to automatically spin up a MongoDB instance in memory. **No database installation or setup is required.**
- **Mongoose ODM**: Provides elegant schema definition and data modeling for MongoDB.
- **Full CRUD Functionality**: Endpoints for Creating, Reading, Updating, and Deleting users.
- **Input Validation**: Uses `express-validator` to validate and sanitize incoming request data.
- **Error Handling**: A custom middleware catches and handles unexpected server errors gracefully.

## Setup and Usage

1.  **Install Node.js**: Ensure you have Node.js (version 14 or higher) installed on your system.

2.  **Install Dependencies**: Navigate to the project directory in your terminal and run:
    ```bash
    npm install
    ```

3.  **Run the Server**: 
    You can start the server in two ways:

    **For development (restarts automatically on file changes):**
    ```bash
    npm run dev
    ```

    **For production:**
    ```bash
    npm start
    ```
    The server will start, connect to the in-memory database, and be available at `http://localhost:3000`.

## API Endpoints

Here is how to interact with the API using `curl`. 

*(Note: Replace `:id` with the actual `_id` of a user returned by the API)*

### 1. Create a User

```bash
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{"name": "John Doe", "email": "john.doe@example.com", "age": 30}'
```

### 2. Get All Users

```bash
curl http://localhost:3000/users
```

### 3. Get a Single User

```bash
curl http://localhost:3000/users/:id
```

### 4. Update a User

```bash
curl -X PUT http://localhost:3000/users/:id -H "Content-Type: application/json" -d '{"name": "Johnathan Doe", "age": 31}'
```

### 5. Delete a User

```bash
curl -X DELETE http://localhost:3000/users/:id
```
