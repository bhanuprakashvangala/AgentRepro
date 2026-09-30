# JWT Auth REST API

This FastAPI project demonstrates JWT-based authentication with bcrypt-hashed passwords. It exposes login/logout endpoints, protects routes with token verification, and includes a helper route to fetch the authenticated user.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --reload
```

The API starts at `http://127.0.0.1:8000`. A sample user `alice` with password `wonderland` is preloaded.

## Authentication flow

1. **Register (optional)**
   ```bash
   curl -X POST http://127.0.0.1:8000/register \
        -H "Content-Type: application/json" \
        -d '{"username": "bob", "password": "secret"}'
   ```

2. **Login** (returns JWT access token valid for 30 minutes)
   ```bash
   TOKEN=$(curl -s -X POST http://127.0.0.1:8000/login \
        -H "Content-Type: application/json" \
        -d '{"username": "alice", "password": "wonderland"}' | jq -r '.access_token')
   ```

3. **Access protected route**
   ```bash
   curl http://127.0.0.1:8000/protected -H "Authorization: Bearer $TOKEN"
   ```

4. **Logout** (revokes the presented token for the demo process lifetime)
   ```bash
   curl -X POST http://127.0.0.1:8000/logout -H "Authorization: Bearer $TOKEN"
   ```

Use the `/me` endpoint to verify the authenticated user details. The `main.py` script can also hash a password when run directly: `python main.py mypassword`.
