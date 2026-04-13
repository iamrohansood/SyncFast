from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str

    class Config:
        orm_mode = True
