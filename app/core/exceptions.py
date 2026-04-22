"""
Custom Exception Classes for Better Error Handling
"""
from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Base custom HTTP exception"""
    pass


class UnauthorizedException(CustomHTTPException):
    """401 Unauthorized"""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(CustomHTTPException):
    """403 Forbidden"""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(CustomHTTPException):
    """404 Not Found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class BadRequestException(CustomHTTPException):
    """400 Bad Request"""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictException(CustomHTTPException):
    """409 Conflict - Resource already exists"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InternalServerErrorException(CustomHTTPException):
    """500 Internal Server Error"""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class UserAlreadyExistsException(ConflictException):
    """User with this email already exists"""
    def __init__(self):
        super().__init__(detail="User with this email already exists")


class InvalidCredentialsException(UnauthorizedException):
    """Invalid email or password"""
    def __init__(self):
        super().__init__(detail="Incorrect email or password")


class TokenExpiredException(UnauthorizedException):
    """JWT Token has expired"""
    def __init__(self):
        super().__init__(detail="Token has expired")


class InvalidTokenException(UnauthorizedException):
    """Invalid JWT Token"""
    def __init__(self):
        super().__init__(detail="Could not validate credentials")


class CompanyInfoAlreadyExistsException(ConflictException):
    """Company info already exists for this user"""
    def __init__(self):
        super().__init__(detail="Company info already exists")
