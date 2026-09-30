import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import gql from 'graphql-tag';

// Type definitions
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    age: Int
    posts: [Post!]!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    published: Boolean!
    authorId: ID!
    author: User!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
    posts: [Post!]!
    post(id: ID!): Post
  }

  type Mutation {
    createUser(name: String!, email: String!, age: Int): User!
    createPost(title: String!, content: String!, authorId: ID!, published: Boolean): Post!
  }
`;

// In-memory data store
const users = [
  { id: '1', name: 'Alice Johnson', email: 'alice@example.com', age: 28 },
  { id: '2', name: 'Bob Smith', email: 'bob@example.com', age: 34 },
  { id: '3', name: 'Charlie Brown', email: 'charlie@example.com', age: 25 }
];

const posts = [
  { id: '1', title: 'GraphQL Basics', content: 'Introduction to GraphQL', published: true, authorId: '1' },
  { id: '2', title: 'Apollo Server Guide', content: 'How to use Apollo Server', published: true, authorId: '1' },
  { id: '3', title: 'JavaScript Tips', content: 'Advanced JS techniques', published: false, authorId: '2' }
];

let nextUserId = 4;
let nextPostId = 4;

// Resolvers
const resolvers = {
  Query: {
    users: () => users,
    user: (_, { id }) => {
      const user = users.find(u => u.id === id);
      if (!user) throw new Error(`User with id ${id} not found`);
      return user;
    },
    posts: () => posts,
    post: (_, { id }) => {
      const post = posts.find(p => p.id === id);
      if (!post) throw new Error(`Post with id ${id} not found`);
      return post;
    }
  },

  Mutation: {
    createUser: (_, { name, email, age }) => {
      const newUser = {
        id: String(nextUserId++),
        name,
        email,
        age: age || null
      };
      users.push(newUser);
      return newUser;
    },
    createPost: (_, { title, content, authorId, published }) => {
      const author = users.find(u => u.id === authorId);
      if (!author) throw new Error(`Author with id ${authorId} not found`);

      const newPost = {
        id: String(nextPostId++),
        title,
        content,
        published: published !== undefined ? published : false,
        authorId
      };
      posts.push(newPost);
      return newPost;
    }
  },

  User: {
    posts: (user) => posts.filter(p => p.authorId === user.id)
  },

  Post: {
    author: (post) => users.find(u => u.id === post.authorId)
  }
};

// Create Apollo Server
const server = new ApolloServer({
  typeDefs,
  resolvers,
});

// Start server
const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 },
});

console.log(`🚀 GraphQL Server ready at ${url}`);
console.log('\nExample queries:');
console.log('  query { users { id name email } }');
console.log('  query { user(id: "1") { name posts { title } } }');
console.log('  mutation { createUser(name: "Dave", email: "dave@example.com", age: 30) { id name } }');
