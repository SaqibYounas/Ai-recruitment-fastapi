from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlmodel import Session, select
from core.settings import settings
from app.schemas.auth import UserSignup, CompanyInfo
from app.schemas.auth import RegisterResponse, CompanyResponse, UserOut
from app.models.auth import User, Company
from app.db.session import get_session
from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_user(user_data: UserSignup, session: Session) -> RegisterResponse:
    hash_password = password_hasher.hash(user_data.password)
    save_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password
    )
    session.add(save_user)
    session.commit()
    session.refresh(save_user)
    return RegisterResponse(
        message="Account created successfully",
        user=UserOut.model_validate(save_user)
    )

def user_login(form_data: OAuth2PasswordRequestForm, session: Session) -> User | None:
    statement = select(User).where(User.email == form_data.username)
    db_user = session.exec(statement).scalar_one_or_none()
    if not db_user:
        return None
    if not password_hasher.verify(form_data.password, db_user.password):
        return None
    return db_user

def add_company_info(company_data: CompanyInfo, session: Session) -> CompanyResponse | None:
    db_user = session.get(User, company_data.user_id)
    if not db_user:
        return None
    if db_user.company_id is not None:
        return CompanyResponse(message="Company info already exists", user=UserOut.model_validate(db_user))
    
    new_company = Company(
        company_name=company_data.companyName,
        position=company_data.position,
        company_size=company_data.companySize,
        industry_type=company_data.industryType,
        location=company_data.location
    )
    session.add(new_company)
    session.flush() 
    db_user.company_id = new_company.id
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return CompanyResponse(message="Company info saved successfully", user=UserOut.model_validate(db_user))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    statement = select(User).where(User.email == email)
    user = session.exec(statement).one_or_none()
    if user is None:
        raise credentials_exception
    return user