import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

// Secret key for JWT (in production, use environment variable)
const JWT_SECRET = 'your-secret-key-change-this-in-production';
const JWT_EXPIRES_IN = '24h';

// In-memory database (replace with real database in production)
const users = [];
const posts = [];
let userIdCounter = 1;
let postIdCounter = 1;

// GraphQL Schema
const typeDefs = `#graphql
  type User {
    id: ID!
    username: String!
    email: String!
    posts: [Post!]!
    createdAt: String!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
    createdAt: String!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  type Query {
    me: User
    user(id: ID!): User
    users: [User!]!
    post(id: ID!): Post
    posts: [Post!]!
    myPosts: [Post!]!
  }

  type Mutation {
    register(username: String!, email: String!, password: String!): AuthPayload!
    login(email: String!, password: String!): AuthPayload!
    createPost(title: String!, content: String!): Post!
    updatePost(id: ID!, title: String, content: String): Post!
    deletePost(id: ID!): Boolean!
  }
`;

// Helper function to generate JWT token
function generateToken(userId) {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

// Helper function to verify JWT token
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

// Helper function to get user from token
function getUserFromToken(token) {
  if (!token) return null;

  const decoded = verifyToken(token);
  if (!decoded) return null;

  return users.find(user => user.id === decoded.userId);
}

// Resolvers
const resolvers = {
  Query: {
    me: (_, __, context) => {
      if (!context.user) throw new Error('Not authenticated');
      return context.user;
    },
    user: (_, { id }) => {
      const user = users.find(u => u.id === id);
      if (!user) throw new Error('User not found');
      return user;
    },
    users: () => users,
    post: (_, { id }) => {
      const post = posts.find(p => p.id === id);
      if (!post) throw new Error('Post not found');
      return post;
    },
    posts: () => posts,
    myPosts: (_, __, context) => {
      if (!context.user) throw new Error('Not authenticated');
      return posts.filter(post => post.authorId === context.user.id);
    }
  },

  Mutation: {
    register: async (_, { username, email, password }) => {
      if (username.length < 3) throw new Error('Username must be at least 3 characters');
      if (!email.includes('@')) throw new Error('Invalid email');
      if (password.length < 6) throw new Error('Password must be at least 6 characters');
      if (users.find(u => u.email === email)) throw new Error('User already exists');

      const hashedPassword = await bcrypt.hash(password, 10);
      const user = {
        id: String(userIdCounter++),
        username,
        email,
        password: hashedPassword,
        createdAt: new Date().toISOString()
      };
      users.push(user);
      return { token: generateToken(user.id), user };
    },

    login: async (_, { email, password }) => {
      const user = users.find(u => u.email === email);
      if (!user) throw new Error('Invalid credentials');
      const valid = await bcrypt.compare(password, user.password);
      if (!valid) throw new Error('Invalid credentials');
      return { token: generateToken(user.id), user };
    },

    createPost: (_, { title, content }, context) => {
      if (!context.user) throw new Error('Not authenticated');
      if (!title.trim() || !content.trim()) throw new Error('Title and content required');
      const post = {
        id: String(postIdCounter++),
        title,
        content,
        authorId: context.user.id,
        createdAt: new Date().toISOString()
      };
      posts.push(post);
      return post;
    },

    updatePost: (_, { id, title, content }, context) => {
      if (!context.user) throw new Error('Not authenticated');
      const post = posts.find(p => p.id === id);
      if (!post) throw new Error('Post not found');
      if (post.authorId !== context.user.id) throw new Error('Not authorized');
      if (title !== undefined) post.title = title;
      if (content !== undefined) post.content = content;
      return post;
    },

    deletePost: (_, { id }, context) => {
      if (!context.user) throw new Error('Not authenticated');
      const index = posts.findIndex(p => p.id === id);
      if (index === -1) throw new Error('Post not found');
      if (posts[index].authorId !== context.user.id) throw new Error('Not authorized');
      posts.splice(index, 1);
      return true;
    }
  },

  User: {
    posts: (user) => posts.filter(post => post.authorId === user.id)
  },

  Post: {
    author: (post) => {
      const author = users.find(user => user.id === post.authorId);
      if (!author) throw new Error('Author not found');
      return author;
    }
  }
};

// Create Apollo Server
const server = new ApolloServer({ typeDefs, resolvers });

// Start server with authentication context
const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 },
  context: async ({ req }) => {
    const authHeader = req.headers.authorization || '';
    const token = authHeader.startsWith('Bearer ') ? authHeader.substring(7) : null;
    const user = getUserFromToken(token);
    return { user };
  },
});

console.log(`🚀 Server ready at: ${url}`);
