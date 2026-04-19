from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlmodel import select
from app.schemas.auth import UserSignup, CompanyInfo
from app.schemas.auth import RegisterResponse, CompanyResponse, UserOut
from app.models.user import User, Company
from pwdlib import PasswordHash
from app.db.session import get_session
from sqlmodel import Session
from fastapi import HTTPException, status

password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_user(user_data: UserSignup, session: Session) -> RegisterResponse:
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    hash_password = password_hasher.hash(user_data.password)
    save_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password
    )
    
    try:
        session.add(save_user)
        session.commit()
        session.refresh(save_user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the account."
        )

    return RegisterResponse(
        message="Account created successfully",
        user=UserOut.model_validate(save_user)
    )


def user_login(form_data: OAuth2PasswordRequestForm, session: get_session) -> User | None:
    statement = select(User).where(User.email == form_data.username)
    results = session.exec(statement)
    db_user = results.first() 

    if not db_user:
        return None

    if not password_hasher.verify(form_data.password, db_user.password):
        return None

    return db_user

def add_company_info(company_data: CompanyInfo, session: Session, current_user: User) -> CompanyResponse | None:
    db_user = session.get(User, current_user.id)
    if not db_user:
        return None
        
    if db_user.company_id is not None:
        return CompanyResponse(
            message="Company info already exists", 
            user=UserOut.model_validate(db_user)
        )
    
    new_company = Company(
        company_name=company_data.companyName,
        position=company_data.position,
        company_size=company_data.companySize,
        industry_type=company_data.industryType,
        location=company_data.location,
    )
    
    session.add(new_company)
    session.flush() 
    db_user.company_id = new_company.id
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return CompanyResponse(
        message="Company info saved successfully", 
        user=UserOut.model_validate(db_user)
    )