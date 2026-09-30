const bcrypt = require('bcrypt');

const saltRounds = 10; // Configurable salt rounds

// Function to hash a password
const hashPassword = async (password) => {
    try {
        const salt = await bcrypt.genSalt(saltRounds);
        const hash = await bcrypt.hash(password, salt);
        return hash;
    } catch (error) {
        console.error('Error hashing password:', error);
        throw error;
    }
};

// Function to compare a password with a hash
const comparePassword = async (password, hash) => {
    try {
        const match = await bcrypt.compare(password, hash);
        return match;
    } catch (error) {
        console.error('Error comparing password:', error);
        throw error;
    }
};

// Example usage
const example = async () => {
    const myPassword = 'my-super-secret-password';

    const hashedPassword = await hashPassword(myPassword);
    console.log('Hashed password:', hashedPassword);

    const isMatch = await comparePassword(myPassword, hashedPassword);
    console.log('Passwords match:', isMatch);

    const isNotMatch = await comparePassword('wrong-password', hashedPassword);
    console.log('Passwords match:', isNotMatch);
};

example();
