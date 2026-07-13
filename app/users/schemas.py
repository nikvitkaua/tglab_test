from pydantic import BaseModel, EmailStr, Field
from app.users.models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль має бути не менше 6 символів")
    role: UserRole

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
