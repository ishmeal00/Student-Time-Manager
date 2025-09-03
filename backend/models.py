# models.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import uuid

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    name: Optional[str] = None
    hashed_password: str

    pages: list["Page"] = Relationship(back_populates="owner")

class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True, nullable=False)
    title: str
    content: str  # JSON string or markdown
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="pages")
