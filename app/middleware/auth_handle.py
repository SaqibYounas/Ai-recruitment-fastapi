"""
Authentication Middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlmodel import select

import jwt
from app.core.settings import settings
from app.core.constants import PUBLIC_ROUTES
from app.models.user import User
from app.db.session import SessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware for protected routes
    
    Args:
        request: HTTP request
        call_next: Next middleware/route handler
        
    Returns:
        Response from next middleware/route handler
    """
    # Check if route is public
    if request.url.path in PUBLIC_ROUTES or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
        return await call_next(request)
    
    # Get token from cookies
    token = request.cookies.get("access_token")
    if not token:
        logger.warning(f"Unauthorized access attempt to {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Unauthorized: No token found",
                "error_code": "NO_TOKEN"
            }
        )
    
    try:
        # Remove Bearer prefix if present
        token = token.replace("Bearer ", "")
        
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        
        if not email:
            logger.warning("Token validation failed: no email in payload")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": "Invalid token",
                    "error_code": "INVALID_TOKEN"
                }
            )
        
        # Get user from database
        with SessionLocal() as session:
            statement = select(User).where(User.email == email)
            user = session.exec(statement).one_or_none()
            
            if not user:
                logger.warning(f"User not found for email: {email}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "message": "User not found",
                        "error_code": "USER_NOT_FOUND"
                    }
                )
            
            # Store user in request state
            request.state.user = user
            request.state.user_id = str(user.id)
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Token has expired",
                "error_code": "TOKEN_EXPIRED"
            }
        )
    
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Invalid token",
                "error_code": "INVALID_TOKEN"
            }
        )
    
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    return await call_next(request)
