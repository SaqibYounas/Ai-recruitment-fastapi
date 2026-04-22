"""
Authentication Services
"""
from sqlmodel import select, Session

from app.schemas.auth import (
    UserRegisterRequest,
    CompanyInfoCreate,
    UserResponse,
    CompanyInfoResponse,
)
from app.models.user import User, Company
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logger import get_logger
from app.core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    CompanyInfoAlreadyExistsException,
    NotFoundException,
)
from datetime import timedelta
from app.core.settings import settings

logger = get_logger(__name__)


def register_user(user_data: UserRegisterRequest, session: Session) -> tuple[User, str]:
    """
    Register a new user
    
    Args:
        user_data: User registration data
        session: Database session
        
    Returns:
        Tuple of (created_user, access_token)
        
    Raises:
        UserAlreadyExistsException: If user already exists
    """
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise UserAlreadyExistsException()
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
    )
    
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"User registered successfully: {user_data.email}")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email},
            expires_delta=access_token_expires,
        )
        
        return new_user, access_token
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error registering user: {str(e)}")
        raise


def authenticate_user(email: str, password: str, session: Session) -> User:
    """
    Authenticate user with email and password
    
    Args:
        email: User email
        password: Plain password
        session: Database session
        
    Returns:
        User object if authentication successful
        
    Raises:
        InvalidCredentialsException: If credentials are invalid
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).one_or_none()
    
    if not user:
        logger.warning(f"Login attempt with non-existent email: {email}")
        raise InvalidCredentialsException()
    
    if not verify_password(password, user.password):
        logger.warning(f"Login attempt with wrong password for email: {email}")
        raise InvalidCredentialsException()
    
    logger.info(f"User authenticated successfully: {email}")
    return user


def add_company_info(
    company_data: CompanyInfoCreate,
    session: Session,
    user: User,
) -> User:
    """
    Add company information to user
    
    Args:
        company_data: Company information data
        session: Database session
        user: Current user
        
    Returns:
        Updated user object
        
    Raises:
        CompanyInfoAlreadyExistsException: If company info already exists
        NotFoundException: If user not found
    """
    # Verify user exists
    db_user = session.get(User, user.id)
    if not db_user:
        logger.error(f"User not found: {user.id}")
        raise NotFoundException(detail="User not found")
    
    # Check if company info already exists
    if db_user.company_id is not None:
        logger.warning(f"User already has company info: {user.id}")
        raise CompanyInfoAlreadyExistsException()
    
    # Create company
    new_company = Company(
        company_name=company_data.company_name,
        position=company_data.position,
        company_size=company_data.company_size,
        industry_type=company_data.industry_type,
        location=company_data.location,
    )
    
    try:
        session.add(new_company)
        session.flush()
        
        # Link company to user
        db_user.company_id = new_company.id
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        logger.info(f"Company info added for user: {user.id}")
        return db_user
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding company info: {str(e)}")
        raise
