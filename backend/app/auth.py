from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from database import users, database
import bcrypt

SECRET_KEY = "kNznW1jvdpSGgzLHCjBk2let929CWJP3PYusp77RkAA"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def authenticate_user(username: str, password: str):
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None
    return user

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    query = users.select().where(users.c.id == int(user_id))
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(401, "User not found")
    return user