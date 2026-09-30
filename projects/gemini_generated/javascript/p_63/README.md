# Password Hashing Service

This project is a password hashing service with bcrypt.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Run the script:

    ```bash
    npm start
    ```

2.  The script will demonstrate how to hash a password and compare it with the original password.

### Functions

-   `hashPassword(password)`: Hashes a password with a configurable number of salt rounds.
-   `comparePassword(password, hash)`: Compares a password with a hash.
