from schemas.auth import UserSignup
from models.auth import User
from sqlmodel import Session



def create_user(user_data: UserSignup, session: Session):

    db_user = User(
    name=user_data.name,
    email=user_data.email,
    password=user_data.password
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user
