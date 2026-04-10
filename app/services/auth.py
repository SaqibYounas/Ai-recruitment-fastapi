from schemas.auth import UserSignup
from models.auth import User


def create_user(user_data:UserSignup):
     db_user = User(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password
    )
     
     
