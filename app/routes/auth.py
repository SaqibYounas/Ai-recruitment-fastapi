from fastapi import Depends
from sqlmodel import Session
from app.db.session import get_session
from services.auth import create_user
from fastapi import FastAPI
from models.auth import User

app = FastAPI()


@app.post("/signup")
def signup(user: User, session: Session =Depends(get_session)):
    return create_user(user, session)
