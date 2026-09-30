const { ApolloServer, gql } = require('apollo-server');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const JWT_SECRET = 'my-super-secret-key';

// In-memory user data (replace with a database in a real application)
const users = [
    {
        id: '1',
        username: 'admin',
        password: bcrypt.hashSync('password', 10)
    }
];

const typeDefs = gql`
    type Query {
        hello: String
        protected: String
    }

    type Mutation {
        login(username: String!, password: String!): String
    }
`;

const resolvers = {
    Query: {
        hello: () => 'Hello, world!',
        protected: (parent, args, context) => {
            if (!context.user) {
                throw new Error('You must be logged in to access this.');
            }
            return `Hello, ${context.user.username}! This is a protected resource.`;
        }
    },
    Mutation: {
        login: (parent, { username, password }) => {
            const user = users.find(u => u.username === username);
            if (!user || !bcrypt.compareSync(password, user.password)) {
                throw new Error('Invalid credentials');
            }
            const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
            return token;
        }
    }
};

const server = new ApolloServer({
    typeDefs,
    resolvers,
    context: ({ req }) => {
        const token = req.headers.authorization || '';
        if (token) {
            try {
                const user = jwt.verify(token.replace('Bearer ', ''), JWT_SECRET);
                return { user };
            } catch (e) {
                console.error(e);
            }
        }
    }
});

server.listen().then(({ url }) => {
    console.log(`🚀 Server ready at ${url}`);
});
