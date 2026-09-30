# GraphQL API with JWT Authentication

Apollo Server (Express) GraphQL API featuring JWT-based authentication, queries, mutations, and error handling.

## Setup
```bash
npm install
npm start
```
Server runs on `http://localhost:4000/graphql` by default.

Set `JWT_SECRET` env variable to customize signing key.

## Example Queries
```graphql
mutation Register {
  register(name: "Charlie", email: "charlie@example.com", password: "secret123") {
    token
    user { id name email role }
  }
}
```

Use returned token in `Authorization: Bearer <token>` header for authenticated requests:
```graphql
query Me {
  me { id name email role }
}

mutation CreatePost {
  createPost(content: "GraphQL is awesome!") {
    id
    content
    author { name }
  }
}
```

Admins (user `alice@example.com`, password `password123`) can query all users:
```graphql
query Users {
  users { id name email role }
}
```

Tokens expire in 1 hour; errors formatted with message and code fields.
