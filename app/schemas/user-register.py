from pydantic import BaseModel,EmailStr


class UserRegister(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
