# main.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from database import init_db, engine, get_session
import crud, models
from schemas import UserCreate, UserRead, Token, PageCreate, PageRead, PageUpdate
from typing import List, Optional
from auth import create_access_token, decode_access_token

app = FastAPI(title="Student Time Manager - Notion-like MVP")

@app.on_event("startup")
def on_start():
    init_db()

# ---------- Auth / Users ----------
@app.post("/auth/register", response_model=UserRead)
def register(payload: UserCreate, session: Session = Depends(get_session)):
    existing = crud.get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(session, payload.email, payload.password, payload.name)
    return UserRead(id=user.id, email=user.email, name=user.name)

@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = crud.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)

# Helper to get current user (very simple)
def get_current_user(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid auth header")
    data = decode_access_token(token)
    if not data or not data.user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.get(models.User, int(data.user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ---------- Pages CRUD ----------
@app.post("/pages/", response_model=PageRead)
def create_page(payload: PageCreate, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    # owner must match current_user or be omitted
    owner_id = payload.owner_id or current_user.id
    page = crud.create_page(session, payload.title, payload.content, owner_id)
    return PageRead(**page.dict())

@app.get("/pages/{uid}", response_model=PageRead)
def read_page(uid: str, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    page = crud.get_page_by_uid(session, uid)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    # optional: enforce owner-only access
    if page.owner_id and page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return PageRead(**page.dict())

@app.get("/pages/", response_model=List[PageRead])
def read_pages(owner_id: Optional[int] = None, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    pages = crud.list_pages(session, owner_id=owner_id or current_user.id)
    return [PageRead(**p.dict()) for p in pages]

@app.patch("/pages/{uid}", response_model=PageRead)
def patch_page(uid: str, payload: PageUpdate, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    page = crud.get_page_by_uid(session, uid)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if page.owner_id and page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    updated = crud.update_page(session, page, title=payload.title, content=payload.content)
    return PageRead(**updated.dict())

@app.delete("/pages/{uid}")
def remove_page(uid: str, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    page = crud.get_page_by_uid(session, uid)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if page.owner_id and page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    crud.delete_page(session, page)
    return {"ok": True, "message": "Page deleted"}

# ---------- Simple health + sample ----------
@app.get("/")
def root():
    return {"status": "ok", "msg": "Student Time Manager API running"}
