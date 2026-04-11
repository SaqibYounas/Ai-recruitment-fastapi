from app.schemas.auth import UserSignup, CompanyInfo, UserLogin
from app.schemas.auth import RegisterResponse, CompanyResponse, LoginResponse, UserOut
from app.models.auth import User, Company
from sqlmodel import Session, select
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

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


def add_company_info(company_data: CompanyInfo, session: Session) -> CompanyResponse | None:
    db_user = session.get(User, company_data.user_id)
    if not db_user:
        return None
    

    if db_user.company_id is not None:
        return CompanyResponse(
        message="Company info already successfully",
        user=UserOut.model_validate(db_user)
    ) 

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

    return CompanyResponse(
        message="Company info saved successfully",
        user=UserOut.model_validate(db_user)
    )


def user_login(user_data: UserLogin, session: Session) -> LoginResponse | None:
    statement = select(User).where(User.email == user_data.email)
    db_user = session.execute(statement).scalar_one_or_none()

    if not db_user:
        return None

    is_valid = password_hasher.verify(user_data.password,db_user.password)

    if not is_valid:
        return None

    return LoginResponse(
        message="Login successful",
        user=UserOut.model_validate(db_user)
    )