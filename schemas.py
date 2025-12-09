from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str
    # age: int
    account_type: str

class UserLogin(UserBase):
    password: str