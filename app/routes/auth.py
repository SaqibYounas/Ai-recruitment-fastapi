from fastapi import Depends
from sqlmodel import Session
from app.services.auth import create_user
from fastapi  import FastAPI ,APIRouter
from app.schemas.auth import UserSignup
from fastapi import Depends
from app.db.session import get_session
from fastapi_limiter.depends import RateLimiter
app = FastAPI()

routes=APIRouter(prefix=("/auth"))

@routes.post("/signup")
def signup(user: UserSignup, session: Session =Depends(get_session)):
    return create_user(user, session)
