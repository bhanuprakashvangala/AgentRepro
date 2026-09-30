# Bcrypt Password Service

Express service for hashing and verifying passwords with configurable salt rounds.

## Setup
```bash
npm install
SALT_ROUNDS=12 npm start
```
Default `SALT_ROUNDS` is 12 if unset.

## Endpoints
### POST /hash
```json
{ "password": "secret" }
```
Returns `{ hash, saltRounds }`.

### POST /compare
```json
{ "password": "secret", "hash": "$2b$12$..." }
```
Returns `{ match: true|false }`.

### GET /
Status endpoint returning configured salt rounds.

## Notes
- Uses `bcrypt.hash()`/`compare()` with async APIs.
- Adjust `SALT_ROUNDS` for security/performance trade-offs.
