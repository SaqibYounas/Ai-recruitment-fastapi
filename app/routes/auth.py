from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status,Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.settings import settings
from app.db.session import get_session
from app.models.auth import User
from app.schemas.auth import Token, UserOut, UserSignup, RegisterResponse, CompanyInfo, CompanyResponse
from app.services.auth import (
    user_login, 
    create_user, 
    add_company_info,
    get_current_user, 
    create_access_token, 
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/signup", response_model=RegisterResponse)
def signup(user: UserSignup, session: Annotated[Session, Depends(get_session)]):
    return create_user(user, session)

@auth_router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
) -> Token:
    user = user_login(form_data, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False     
    )

    return {"message": "Login successful and cookie set"}

@auth_router.post("/company-info", response_model=CompanyResponse)
def save_company(company: CompanyInfo, session: Annotated[Session, Depends(get_session)]):
    result = add_company_info(company, session)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@auth_router.get("/me", response_model=UserOut)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user