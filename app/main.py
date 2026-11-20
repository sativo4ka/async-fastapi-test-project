from hashlib import pbkdf2_hmac
from secrets import token_urlsafe, token_bytes
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field


app = FastAPI(title="User Profile API", version="1.0.0")

# Для тестового приложения данные хранятся в памяти.
users = {}
tokens = {}


class RegisterData(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=128)
    email: EmailStr
    name: str = Field(min_length=1, max_length=80)


class LoginData(BaseModel):
    username: str
    password: str


class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)


def hash_password(password: str, salt: bytes) -> str:
    return pbkdf2_hmac("sha256", password.encode(), salt, 120_000).hex()


def get_current_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")
    token = authorization.removeprefix("Bearer ").strip()
    username = tokens.get(token)
    if not username or username not in users:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterData):
    if data.username in users:
        raise HTTPException(status_code=409, detail="Username already exists")
    if any(user["email"] == data.email for user in users.values()):
        raise HTTPException(status_code=409, detail="Email already exists")

    salt = token_bytes(16)
    users[data.username] = {
        "password_salt": salt,
        "password_hash": hash_password(data.password, salt),
        "email": str(data.email),
        "name": data.name,
    }
    token = token_urlsafe(32)
    tokens[token] = data.username
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/login")
async def login(data: LoginData):
    user = users.get(data.username)
    if not user or hash_password(data.password, user["password_salt"]) != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = token_urlsafe(32)
    tokens[token] = data.username
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/profile")
async def get_profile(authorization: Optional[str] = Header(default=None)):
    username = get_current_user(authorization)
    user = users[username]
    return {"username": username, "email": user["email"], "name": user["name"]}


@app.put("/api/profile")
async def update_profile(
    data: ProfileUpdate,
    authorization: Optional[str] = Header(default=None),
):
    username = get_current_user(authorization)
    user = users[username]

    if data.email is not None:
        if any(
            other_username != username and other_user["email"] == str(data.email)
            for other_username, other_user in users.items()
        ):
            raise HTTPException(status_code=409, detail="Email already exists")
        user["email"] = str(data.email)

    if data.name is not None:
        user["name"] = data.name

    return {"username": username, "email": user["email"], "name": user["name"]}


@app.post("/api/logout")
async def logout(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")
    token = authorization.removeprefix("Bearer ").strip()
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    del tokens[token]
    return {"message": "Logged out"}
