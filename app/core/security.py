"""
Security and Authentication Module
"""
from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.settings import settings
from app.core.logger import get_logger
from app.core.exceptions import InvalidTokenException, TokenExpiredException

logger = get_logger(__name__)

# Password hashing
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash password using recommended algorithm
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {str(e)}")
        raise


def decode_token(token: str) -> Optional[str]:
    """
    Decode JWT token and extract email
    
    Args:
        token: JWT token to decode
        
    Returns:
        Email from token payload
        
    Raises:
        InvalidTokenException: If token is invalid
        TokenExpiredException: If token has expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: str = payload.get("sub")
        
        if email is None:
            raise InvalidTokenException()
        
        return email
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise TokenExpiredException()
    except InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise InvalidTokenException()
    except Exception as e:
        logger.error(f"Token decode error: {str(e)}")
        raise InvalidTokenException()


# For backward compatibility
verify_token = decode_token
