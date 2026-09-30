import 'dotenv/config';
import express from 'express';
import session from 'express-session';
import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';
import { Strategy as GitHubStrategy } from 'passport-github2';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 3000;
const SESSION_SECRET = process.env.SESSION_SECRET || 'change-me-secret';

const app = express();

const users = new Map();

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser((id, done) => {
  const user = users.get(id);
  done(null, user || false);
});

if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  passport.use(
    new GoogleStrategy(
      {
        clientID: process.env.GOOGLE_CLIENT_ID,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        callbackURL: process.env.GOOGLE_CALLBACK_URL || 'http://localhost:3000/auth/google/callback'
      },
      (accessToken, refreshToken, profile, done) => {
        const user = {
          id: `google-${profile.id}`,
          provider: 'google',
          displayName: profile.displayName,
          emails: profile.emails,
          photos: profile.photos,
          profile
        };
        users.set(user.id, user);
        return done(null, user);
      }
    )
  );
} else {
  console.warn('Google OAuth credentials not set. GOOGLE_CLIENT_ID/SECRET required.');
}

if (process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET) {
  passport.use(
    new GitHubStrategy(
      {
        clientID: process.env.GITHUB_CLIENT_ID,
        clientSecret: process.env.GITHUB_CLIENT_SECRET,
        callbackURL: process.env.GITHUB_CALLBACK_URL || 'http://localhost:3000/auth/github/callback'
      },
      (accessToken, refreshToken, profile, done) => {
        const user = {
          id: `github-${profile.id}`,
          provider: 'github',
          displayName: profile.displayName || profile.username,
          emails: profile.emails,
          photos: profile.photos,
          profile
        };
        users.set(user.id, user);
        return done(null, user);
      }
    )
  );
} else {
  console.warn('GitHub OAuth credentials not set. GITHUB_CLIENT_ID/SECRET required.');
}

app.use(
  session({
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false
  })
);

app.use(passport.initialize());
app.use(passport.session());

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) {
    return next();
  }
  res.redirect('/');
}

app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get(
  '/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/' }),
  (req, res) => {
    res.redirect('/profile');
  }
);

app.get('/auth/github', passport.authenticate('github', { scope: ['user:email'] }));

app.get(
  '/auth/github/callback',
  passport.authenticate('github', { failureRedirect: '/' }),
  (req, res) => {
    res.redirect('/profile');
  }
);

app.get('/profile', ensureAuthenticated, (req, res) => {
  const user = req.user;
  res.send(`
    <h1>Profile</h1>
    <p>Logged in via: ${user.provider}</p>
    <pre>${JSON.stringify(user, null, 2)}</pre>
    <a href="/logout">Logout</a>
  `);
});

app.get('/logout', (req, res, next) => {
  req.logout(function (err) {
    if (err) { return next(err); }
    req.session.destroy(() => {
      res.redirect('/');
    });
  });
});

app.listen(PORT, () => {
  console.log(`OAuth server running on http://localhost:${PORT}`);
});
