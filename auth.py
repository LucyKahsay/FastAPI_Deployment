from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

# password_hash
#       ↓
# a tool that can:
#       ↓
# HASH passwords
# and
# CHECK passwords

from config import settings
import hashlib
import secrets


# A way to attach extra information to a parameter.
from typing import Annotated
from fastapi import Depends, HTTPException, status
# FastAPI's instruction for getting a value from another function...for depends

# Annotated → describes the parameter and attaches extra information

# Depends → tells FastAPI WHERE/HOW to get the value

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db



password_hash= PasswordHash.recommended()
# does not hash anybody's password yet.
# It is just creating the tool you'll use later.

# "FastAPI, give me a tool that can get the "
# "user's token from their request."
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl= "api/users/token")



def hash_password(password: str) -> str:
    return password_hash.hash (password)

def verify_password(plain_password: str, hashed_password: str) ->bool:
    return password_hash.verify(plain_password, hashed_password)


def generate_reset_token()-> str:
    return secrets.token_urlsafe(32)
# "Whenever I call this function, "
# "give me a new random reset token."

def hash_reset_token(token: str)-> str:
    return hashlib.sha256(token.encode()).hexdigest()



# create_access_token() takes information about the user,
# adds an expiration time, signs that information with 
# the server's secret key using the chosen algorithm, 
# and returns the resulting JWT.
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes,
        )
        # "Okay, nobody gave me a custom expiration. "
        # "I'll use the default from my settings."
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt

# this function takes token as a parameter 
# and returns a user id if the token is valid 
def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user id) if valid."""
# "Try to execute the following code, but if "
# "something goes wrong, don't crash the whole 
# application — handle the error.
    try:
        # "Take this JWT, verify/read it, and give me the"
        # " information that was inside it. I'll store
        # that information in payload.
        # "Decode this JWT, and while doing so,"
        # " use my secret key and the HS256 "
        # "method to verify that the JWT is legitimate."
        # and what gets saved to the payload is the 
        # user id and the expiration time
        payload = jwt.decode(
            token,   # THE JWT to decode
            settings.secret_key.get_secret_value(),  # secret used to verify it
            algorithms=[settings.algorithm],      # method used for verification
            options={"require": ["exp", "sub"]},   # REQUIRE these claims to exist
            # "Don't accept a token unless it contains both 
            # an expiration (exp) and a subject/user ID (sub).
            # "When you decode this JWT, REQUIRE it to " \
            # "already contain exp and sub."
            # "Before you accept this token, 
            # make sure it contains:exp sub
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")

    


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(models.User).where(models.User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser=Annotated[models.User, Depends(get_current_user)]

    
