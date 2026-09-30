const bcrypt = require('bcrypt');

/**
 * Password Hashing Service
 * Provides secure password hashing and comparison using bcrypt
 */
class PasswordHashingService {
  /**
   * @param {number} saltRounds - Number of rounds for salt generation (default: 10)
   */
  constructor(saltRounds = 10) {
    if (saltRounds < 4 || saltRounds > 31) {
      throw new Error('Salt rounds must be between 4 and 31');
    }
    this.saltRounds = saltRounds;
  }

  /**
   * Hash a password with bcrypt
   * @param {string} password - Plain text password to hash
   * @returns {Promise<string>} Hashed password
   */
  async hashPassword(password) {
    if (!password || typeof password !== 'string') {
      throw new Error('Password must be a non-empty string');
    }

    try {
      const salt = await bcrypt.genSalt(this.saltRounds);
      const hash = await bcrypt.hash(password, salt);
      return hash;
    } catch (error) {
      throw new Error(`Failed to hash password: ${error.message}`);
    }
  }

  /**
   * Hash a password synchronously
   * @param {string} password - Plain text password to hash
   * @returns {string} Hashed password
   */
  hashPasswordSync(password) {
    if (!password || typeof password !== 'string') {
      throw new Error('Password must be a non-empty string');
    }

    try {
      const salt = bcrypt.genSaltSync(this.saltRounds);
      const hash = bcrypt.hashSync(password, salt);
      return hash;
    } catch (error) {
      throw new Error(`Failed to hash password: ${error.message}`);
    }
  }

  /**
   * Compare a plain text password with a hashed password
   * @param {string} password - Plain text password
   * @param {string} hash - Hashed password to compare against
   * @returns {Promise<boolean>} True if passwords match, false otherwise
   */
  async comparePassword(password, hash) {
    if (!password || typeof password !== 'string') {
      throw new Error('Password must be a non-empty string');
    }
    if (!hash || typeof hash !== 'string') {
      throw new Error('Hash must be a non-empty string');
    }

    try {
      const match = await bcrypt.compare(password, hash);
      return match;
    } catch (error) {
      throw new Error(`Failed to compare password: ${error.message}`);
    }
  }

  /**
   * Compare a plain text password with a hashed password synchronously
   * @param {string} password - Plain text password
   * @param {string} hash - Hashed password to compare against
   * @returns {boolean} True if passwords match, false otherwise
   */
  comparePasswordSync(password, hash) {
    if (!password || typeof password !== 'string') {
      throw new Error('Password must be a non-empty string');
    }
    if (!hash || typeof hash !== 'string') {
      throw new Error('Hash must be a non-empty string');
    }

    try {
      const match = bcrypt.compareSync(password, hash);
      return match;
    } catch (error) {
      throw new Error(`Failed to compare password: ${error.message}`);
    }
  }

  /**
   * Get the current salt rounds configuration
   * @returns {number} Current salt rounds
   */
  getSaltRounds() {
    return this.saltRounds;
  }

  /**
   * Update salt rounds configuration
   * @param {number} saltRounds - New salt rounds value
   */
  setSaltRounds(saltRounds) {
    if (saltRounds < 4 || saltRounds > 31) {
      throw new Error('Salt rounds must be between 4 and 31');
    }
    this.saltRounds = saltRounds;
  }
}

module.exports = PasswordHashingService;
