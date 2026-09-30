import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { GraphQLError } from 'graphql';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-me';
const PORT = process.env.PORT || 4000;

const users = [
  { id: '1', name: 'Alice Admin', email: 'alice@example.com', password: 'password123', role: 'ADMIN' },
  { id: '2', name: 'Bob User', email: 'bob@example.com', password: 'password123', role: 'USER' }
];

const posts = [
  { id: '1', content: 'Welcome to the GraphQL API!', authorId: '1' }
];

const typeDefs = `#graphql
  enum Role {
    ADMIN
    USER
  }

  type User {
    id: ID!
    name: String!
    email: String!
    role: Role!
  }

  type Post {
    id: ID!
    content: String!
    author: User!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  type Query {
    me: User
    users: [User!]!
    posts: [Post!]!
  }

  type Mutation {
    register(name: String!, email: String!, password: String!): AuthPayload!
    login(email: String!, password: String!): AuthPayload!
    createPost(content: String!): Post!
  }
`;

const resolvers = {
  Query: {
    me: (_, __, contextValue) => contextValue.user || null,
    users: (_, __, contextValue) => {
      if (!contextValue.user || contextValue.user.role !== 'ADMIN') {
        throw new GraphQLError('Not authorized to view users', {
          extensions: { code: 'FORBIDDEN' }
        });
      }
      return users.map(maskSensitiveFields);
    },
    posts: () => posts.map((post) => ({ ...post }))
  },
  Mutation: {
    register: (_, { name, email, password }) => {
      validateString(name, 'name');
      validateEmail(email);
      validatePassword(password);

      if (users.some((u) => u.email === email)) {
        throw new GraphQLError('Email already registered', { extensions: { code: 'BAD_USER_INPUT' } });
      }
      const newUser = {
        id: String(users.length + 1),
        name,
        email,
        password,
        role: 'USER'
      };
      users.push(newUser);
      const token = signToken(newUser);
      return { token, user: maskSensitiveFields(newUser) };
    },
    login: (_, { email, password }) => {
      validateEmail(email);
      const user = users.find((u) => u.email === email);
      if (!user || user.password !== password) {
        throw new GraphQLError('Invalid credentials', { extensions: { code: 'UNAUTHENTICATED' } });
      }
      const token = signToken(user);
      return { token, user: maskSensitiveFields(user) };
    },
    createPost: (_, { content }, contextValue) => {
      if (!contextValue.user) {
        throw new GraphQLError('Authentication required', { extensions: { code: 'UNAUTHENTICATED' } });
      }
      validateString(content, 'content');
      const newPost = {
        id: String(posts.length + 1),
        content,
        authorId: contextValue.user.id
      };
      posts.push(newPost);
      return newPost;
    }
  },
  Post: {
    author: (post) => {
      const author = users.find((u) => u.id === post.authorId);
      return maskSensitiveFields(author);
    }
  }
};

function validateString(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new GraphQLError(`${field} must be a non-empty string`, {
      extensions: { code: 'BAD_USER_INPUT' }
    });
  }
}

function validateEmail(email) {
  validateString(email, 'email');
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!pattern.test(email)) {
    throw new GraphQLError('Invalid email format', { extensions: { code: 'BAD_USER_INPUT' } });
  }
}

function validatePassword(password) {
  validateString(password, 'password');
  if (password.length < 6) {
    throw new GraphQLError('Password must be at least 6 characters', {
      extensions: { code: 'BAD_USER_INPUT' }
    });
  }
}

function signToken(user) {
  return jwt.sign({ sub: user.id, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
}

function maskSensitiveFields(user) {
  if (!user) return null;
  const { password, ...rest } = user;
  return rest;
}

async function buildContext({ req }) {
  const authHeader = req.headers.authorization || '';
  if (!authHeader.startsWith('Bearer ')) {
    return { user: null };
  }
  const token = authHeader.substring(7);
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    const user = users.find((u) => u.id === payload.sub);
    if (!user) {
      return { user: null };
    }
    return { user: maskSensitiveFields(user) };
  } catch (error) {
    return { user: null };
  }
}

async function startServer() {
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    formatError: (formattedError) => ({
      message: formattedError.message,
      code: formattedError.extensions?.code || 'INTERNAL_SERVER_ERROR'
    })
  });

  await server.start();

  const app = express();
  app.use(cors());
  app.use(bodyParser.json());

  app.use('/graphql', expressMiddleware(server, { context: buildContext }));

  app.get('/', (req, res) => {
    res.json({ status: 'GraphQL server running', endpoint: '/graphql' });
  });

  app.listen(PORT, () => {
    console.log(`🚀 Server ready at http://localhost:${PORT}/graphql`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server', err);
  process.exit(1);
});
