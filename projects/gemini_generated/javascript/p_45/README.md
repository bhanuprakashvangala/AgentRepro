# GraphQL API with Authentication

This project is a GraphQL API with JWT authentication, built with Apollo Server.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Open your browser and go to `http://localhost:4000` to access the Apollo Studio.

### Queries and Mutations

**Login Mutation:**

```graphql
mutation {
  login(username: "admin", password: "password")
}
```

This will return a JWT token.

**Protected Query:**

To access the protected query, you need to include the JWT token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

Then you can run the query:

```graphql
query {
  protected
}
```
