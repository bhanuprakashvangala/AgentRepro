# OAuth2 Authentication Server

Express + Passport.js server supporting Google and GitHub OAuth flows with session management (`express-session`).

## Setup
```bash
npm install
```

Create `.env` with provider credentials:
```
SESSION_SECRET=super-secure-session-secret
PORT=3000

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_CALLBACK_URL=http://localhost:3000/auth/google/callback

GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_CALLBACK_URL=http://localhost:3000/auth/github/callback
```

Obtain credentials from Google Cloud Console and GitHub Developer Settings.

## Run
```bash
npm start
```
Visit `http://localhost:3000` and choose a provider. After authentication, profile data is stored in memory (Map) and exposed at `/profile`. Sessions persist via cookies.

## Routes
- `/auth/google`, `/auth/google/callback`
- `/auth/github`, `/auth/github/callback`
- `/profile` (requires login)
- `/logout`

Modify serialization/deserialization to persist users in a database for production use.
