import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.auth import User
from app.schemas.auth import Token, TokenData, UserOut
from app.services.auth import user_login, create_user

SECRET_KEY = "super-secret-key-123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



# --- ROUTES ---

@auth_router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
) -> Token:
    # user_login service ko form_data pass kar rahe hain
    user = user_login(form_data, session)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_router.get("/me", response_model=UserOut)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user