#!/usr/bin/env python3
"""FastAPI application providing JWT-based authentication with bcrypt-hashed passwords."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Set

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY", "change-me-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

app = FastAPI(title="JWT Auth API", version="1.0.0")

# ----------------------------------------------------------------------------
# In-memory storage (for demo purposes only)
# ----------------------------------------------------------------------------

class UserRecord(BaseModel):
    username: str
    hashed_password: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


users_db: Dict[str, UserRecord] = {
    "alice": UserRecord(username="alice", hashed_password=hash_password("wonderland"))
}

revoked_tokens: Set[str] = set()

# ----------------------------------------------------------------------------
# Pydantic schemas
# ----------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    message: str


class UserInfo(BaseModel):
    username: str


# ----------------------------------------------------------------------------
# JWT helper utilities
# ----------------------------------------------------------------------------


def create_access_token(*, subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed") from exc


# ----------------------------------------------------------------------------
# Dependencies
# ----------------------------------------------------------------------------


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserInfo:
    token = credentials.credentials
    if token in revoked_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    username = decode_token(token)
    user_record = users_db.get(username)
    if not user_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return UserInfo(username=user_record.username)


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------


@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest) -> MessageResponse:
    username = request.username.strip()
    if not username or not request.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    if username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")

    users_db[username] = UserRecord(username=username, hashed_password=hash_password(request.password))
    return MessageResponse(message="User registered successfully")


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    user_record = users_db.get(request.username)
    if not user_record or not verify_password(request.password, user_record.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user_record.username, expires_delta=access_token_expires)
    return TokenResponse(access_token=access_token, expires_in=int(access_token_expires.total_seconds()))


@app.post("/logout", response_model=MessageResponse)
def logout(credentials: HTTPAuthorizationCredentials = Security(security)) -> MessageResponse:
    token = credentials.credentials
    # Ensure the token is valid before revocation.
    decode_token(token)
    revoked_tokens.add(token)
    return MessageResponse(message="Token revoked. Logout successful.")


@app.get("/me", response_model=UserInfo)
def read_users_me(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    return current_user


@app.get("/protected", response_model=MessageResponse)
def protected_route(current_user: UserInfo = Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message=f"Hello, {current_user.username}! This is a protected resource.")


# Root endpoint for sanity check
@app.get("/", response_model=MessageResponse)
def root() -> MessageResponse:
    return MessageResponse(message="JWT Auth API is running. Use /login or /register to get started.")


# ----------------------------------------------------------------------------
# Utility command for generating hashed passwords when run directly
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse as _argparse

    parser = _argparse.ArgumentParser(description="Helper to hash a password using bcrypt (passlib).")
    parser.add_argument("password", help="Plain text password to hash")
    args = parser.parse_args()
    print(hash_password(args.password))
