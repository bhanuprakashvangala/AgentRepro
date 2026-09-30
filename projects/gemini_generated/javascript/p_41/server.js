const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const { MongoMemoryServer } = require('mongodb-memory-server');

const app = express();
const PORT = process.env.PORT || 3000;

// --- Middleware ---
app.use(express.json());

// --- Mongoose Schema and Model ---
const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true
    },
    email: {
        type: String,
        required: true,
        unique: true
    },
    age: {
        type: Number,
        min: 18
    }
});
const User = mongoose.model('User', userSchema);

// --- Input Validation Rules ---
const userValidationRules = [
    body('name').notEmpty().withMessage('Name is required'),
    body('email').isEmail().withMessage('Must be a valid email address'),
    body('age').optional().isInt({ min: 18 }).withMessage('Age must be a number and at least 18')
];

// --- CRUD Routes ---

// CREATE a new user
app.post('/users', userValidationRules, async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }
    try {
        const user = new User(req.body);
        await user.save();
        res.status(201).send(user);
    } catch (error) {
        // Pass error to the error handling middleware
        next(error);
    }
});

// READ all users
app.get('/users', async (req, res, next) => {
    try {
        const users = await User.find();
        res.send(users);
    } catch (error) {
        next(error);
    }
});

// READ a single user by ID
app.get('/users/:id', async (req, res, next) => {
    try {
        const user = await User.findById(req.params.id);
        if (!user) {
            return res.status(404).send({ message: 'User not found' });
        }
        res.send(user);
    } catch (error) {
        next(error);
    }
});

// UPDATE a user by ID
app.put('/users/:id', userValidationRules, async (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }
    try {
        const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
        if (!user) {
            return res.status(404).send({ message: 'User not found' });
        }
        res.send(user);
    } catch (error) {
        next(error);
    }
});

// DELETE a user by ID
app.delete('/users/:id', async (req, res, next) => {
    try {
        const user = await User.findByIdAndDelete(req.params.id);
        if (!user) {
            return res.status(404).send({ message: 'User not found' });
        }
        res.send({ message: 'User deleted successfully' });
    } catch (error) {
        next(error);
    }
});

// --- Global Error Handling Middleware ---
// This middleware should be last
app.use((err, req, res, next) => {
    console.error(err.stack);
    // Handle Mongoose duplicate key error
    if (err.code === 11000) {
        return res.status(400).json({ message: 'Email already exists.' });
    }
    res.status(500).send('Something broke!');
});

// --- Server and DB Initialization ---
const startServer = async () => {
    try {
        // Spin up an in-memory MongoDB server
        const mongoServer = await MongoMemoryServer.create();
        const mongoUri = mongoServer.getUri();

        // Connect Mongoose to the in-memory server
        await mongoose.connect(mongoUri);
        console.log('Connected to in-memory MongoDB!');

        // Start the Express server
        app.listen(PORT, () => {
            console.log(`Server running on http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error('Failed to start server or DB', error);
        process.exit(1);
    }
};

startServer();
