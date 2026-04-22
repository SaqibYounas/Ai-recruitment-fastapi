"""
Main FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.settings import settings
from app.core.logger import get_logger
from app.core.constants import API_V1_PREFIX
from app.config.dbconnection import engine
from app.models.user import create_db
from app.routes.auth import auth_router
from app.routes.job import job_router
from app.routes.application import app_router
from app.routes.subscription import subscription_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting up AI Recruitment System")
    create_db(engine)
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Recruitment System")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Recruitment AI Portal",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Include authentication routes (no prefix for backward compatibility)
app.include_router(auth_router)

# Include versioned API routes
app.include_router(
    job_router,
    prefix=f"{API_V1_PREFIX}/jobs",
    tags=["Jobs"]
)

app.include_router(
    app_router,
    prefix=f"{API_V1_PREFIX}/applications",
    tags=["Applications"]
)

app.include_router(
    subscription_router,
    prefix=f"{API_V1_PREFIX}/subscriptions",
    tags=["Subscriptions"]
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
