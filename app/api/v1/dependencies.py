"""
Common Dependencies for API Endpoints
"""
from typing import Annotated, Optional
from fastapi import Depends, Cookie, Query, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User
from app.core.security import decode_token
from app.core.exceptions import (
    UnauthorizedException,
    NotFoundException,
    InvalidTokenException,
    TokenExpiredException,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    session: Annotated[Session, Depends(get_session)] = None,
) -> User:
    """
    Get current authenticated user from token
    
    Args:
        access_token: JWT token from cookies
        session: Database session
        
    Returns:
        Current user object
        
    Raises:
        UnauthorizedException: If no token provided
        InvalidTokenException: If token is invalid
        TokenExpiredException: If token has expired
        NotFoundException: If user not found
    """
    if not access_token:
        raise UnauthorizedException(detail="No token provided")
    
    try:
        # Remove Bearer prefix if present
        token = access_token.replace("Bearer ", "")
        email = decode_token(token)
        
        if not email:
            raise InvalidTokenException()
            
    except Exception as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise InvalidTokenException()
    
    # Get user from database
    statement = select(User).where(User.email == email)
    user = session.exec(statement).one_or_none()
    
    if not user:
        raise NotFoundException(detail="User not found")
    
    return user


async def get_optional_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    session: Annotated[Session, Depends(get_session)] = None,
) -> Optional[User]:
    """
    Get optional authenticated user (doesn't fail if no token)
    
    Args:
        access_token: JWT token from cookies
        session: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not access_token:
        return None
    
    try:
        token = access_token.replace("Bearer ", "")
        email = decode_token(token)
        
        if email:
            statement = select(User).where(User.email == email)
            return session.exec(statement).one_or_none()
    except Exception:
        pass
    
    return None


class PaginationDependency:
    """Pagination dependency"""
    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginationDependency:
    """Get pagination dependency"""
    return PaginationDependency(page=page, limit=limit)


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]
PaginationParams = Annotated[PaginationDependency, Depends(get_pagination)]
