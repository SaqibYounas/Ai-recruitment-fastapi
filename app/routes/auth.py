from fastapi import Depends
from sqlmodel import Session
from services.auth import create_user
from fastapi  import FastAPI ,APIRouter
from schemas.auth import UserSignup
from fastapi import Depends
from db.session import get_session
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate

app = FastAPI()
auth = APIRouter()

rate_limiter = Limiter(Rate(2, Duration.SECOND * 5))


@app.post("/signup",dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def signup(user: UserSignup, session: Session =Depends(get_session)):
    return create_user(user, session)
