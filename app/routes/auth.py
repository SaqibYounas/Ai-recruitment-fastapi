from fastapi import Depends, FastAPI, APIRouter
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.auth import UserSignup, UserLogin, CompanyInfo
from app.services.auth import create_user, user_login, add_company_info

app = FastAPI()

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/signup")
def signup_endpoint(user: UserSignup, session: Session = Depends(get_session)):
    return create_user(user, session)

@auth_router.post("/login")
def login_endpoint(user: UserLogin, session: Session = Depends(get_session)):
    return user_login(user, session)

@auth_router.post("/company-info")
def company_info_endpoint(company: CompanyInfo, session: Session = Depends(get_session)):
    return add_company_info(company, session)

app.include_router(auth_router)