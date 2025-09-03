# crud.py
from sqlmodel import Session, select
from models import User, Page
from auth import hash_password, verify_password, create_access_token
from typing import Optional

# ---- Users ----
def create_user(session: Session, email: str, password: str, name: Optional[str] = None) -> User:
    user = User(email=email, name=name, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# ---- Pages ----
def create_page(session: Session, title: str, content: str, owner_id: Optional[int] = None) -> Page:
    page = Page(title=title, content=content, owner_id=owner_id)
    session.add(page)
    session.commit()
    session.refresh(page)
    return page

def get_page_by_uid(session: Session, uid: str) -> Optional[Page]:
    stmt = select(Page).where(Page.uid == uid)
    return session.exec(stmt).first()

def list_pages(session: Session, owner_id: Optional[int] = None):
    stmt = select(Page)
    if owner_id:
        stmt = stmt.where(Page.owner_id == owner_id)
    return session.exec(stmt).all()

def update_page(session: Session, page: Page, title: Optional[str] = None, content: Optional[str] = None):
    if title is not None:
        page.title = title
    if content is not None:
        page.content = content
    session.add(page)
    session.commit()
    session.refresh(page)
    return page

def delete_page(session: Session, page: Page):
    session.delete(page)
    session.commit()
    return True
