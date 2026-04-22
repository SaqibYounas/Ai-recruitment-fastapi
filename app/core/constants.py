"""
Application Constants
"""

# API
API_V1_PREFIX = "/api/v1"
API_TITLE = "AI Recruitment System"
API_DESCRIPTION = "Automated recruitment platform using AI"
API_VERSION = "1.0.0"

# Authentication
TOKEN_TYPE = "bearer"
ALGORITHM = "HS256"

# CORS
DEFAULT_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

# Database
DEFAULT_POOL_SIZE = 10
DEFAULT_MAX_OVERFLOW = 20

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# File Upload
ALLOWED_CV_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_CV_SIZE_MB = 10

# Validation
PASSWORD_MIN_LENGTH = 8
EMAIL_REGEX_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Public Routes (no auth required)
PUBLIC_ROUTES = [
    "/auth/register",
    "/auth/login",
    "/applications/apply",
    "/jobs/all",
    "/docs",
    "/openapi.json",
    "/redoc",
]

# Error Messages
ERROR_USER_NOT_FOUND = "User not found"
ERROR_INVALID_CREDENTIALS = "Incorrect email or password"
ERROR_USER_EXISTS = "User with this email already exists"
ERROR_TOKEN_INVALID = "Could not validate credentials"
ERROR_TOKEN_EXPIRED = "Token has expired"
ERROR_UNAUTHORIZED = "Unauthorized access"
