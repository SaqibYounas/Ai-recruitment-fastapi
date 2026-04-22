"""
Authentication Routes
"""
from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.settings import settings
from app.db.session import get_session
from app.schemas.auth import (
    UserRegisterRequest,
    CompanyInfoCreate,
    TokenResponse,
    RegisterResponse,
    CompanyInfoResponse,
    UserResponse,
)
from app.core.security import create_access_token
from app.models.user import User
from app.services.auth import (
    register_user,
    authenticate_user,
    add_company_info,
)
from app.api.v1.dependencies import CurrentUser
from app.core.logger import get_logger

logger = get_logger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
def register(
    user_data: UserRegisterRequest,
    session: Annotated[Session, Depends(get_session)],
):
    """Register a new user"""
    new_user, access_token = register_user(user_data, session)
    
    # Set secure cookie with token
    response = RegisterResponse(
        message="Account created successfully",
        user=UserResponse.model_validate(new_user)
    )
    
    # Note: Response cookie will be set in main.py response interceptor
    return response


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and receive access token"
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> TokenResponse:
    """
    Authenticate user and return access token
    
    Uses OAuth2 password flow. Token is returned in both response body and secure cookie.
    """
    # Authenticate user
    user = authenticate_user(form_data.username, form_data.password, session)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    
    # Set secure cookie (HTTPOnly for security)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.DEBUG is False,  # Only HTTPS in production
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@auth_router.post(
    "/company-info",
    response_model=CompanyInfoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add company information",
    description="Add or update company information for authenticated user"
)
def save_company_info(
    company_data: CompanyInfoCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    """Add company information to user account"""
    updated_user = add_company_info(company_data, session, current_user)
    
    logger.info(f"Company info saved for user: {current_user.email}")
    
    return CompanyInfoResponse(
        message="Company info saved successfully",
        user=UserResponse.model_validate(updated_user),
    )


@auth_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get current authenticated user's information"
)
def get_current_user_info(
    current_user: CurrentUser,
):
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user by clearing authentication cookie"
)
def logout(response: Response):
    """Logout user by clearing the authentication cookie"""
    response.delete_cookie(key="access_token", secure=settings.DEBUG is False)
    logger.info("User logged out")
    return {"message": "Logged out successfully"}
