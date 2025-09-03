# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str]
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int]

class PageCreate(BaseModel):
    title: str
    content: str
    owner_id: Optional[int] = None

class PageRead(BaseModel):
    id: int
    uid: str
    title: str
    content: str
    owner_id: Optional[int]

class PageUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
