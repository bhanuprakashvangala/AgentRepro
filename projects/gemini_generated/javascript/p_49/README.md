# OAuth2 Authentication Server

This project is an OAuth2 authentication server built with Express, Passport.js, and supports Google and GitHub providers.

## Requirements

- Node.js
- npm
- Google and GitHub developer accounts with OAuth apps created.

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your OAuth credentials:

    ```
    GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
    GITHUB_CLIENT_ID=YOUR_GITHUB_CLIENT_ID
    GITHUB_CLIENT_SECRET=YOUR_GITHUB_CLIENT_SECRET
    SESSION_SECRET=my-session-secret
    ```

    **Important**: For the OAuth providers, you need to set the authorized callback URL to `http://localhost:3000/auth/<provider>/callback` (e.g., `http://localhost:3000/auth/google/callback`).

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Open your browser and go to `http://localhost:3000`.

3.  Click on the links to authenticate with Google or GitHub.
