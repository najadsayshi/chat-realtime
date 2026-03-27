from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.jwt_handler import create_token
from sqlmodel import Session, select
from app.models.db import engine, get_session
from app.models.user import User, UserCreate , UserLogin



router = APIRouter()







@router.post("/signup")
async def signup(request : UserCreate,db :Session = Depends(get_session)):

    email = request.email.lower().strip()
    
    statement = select(User).where(User.email == email)

    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        name = request.name,
        email = email,
        password = request.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_session)):

    email = user.email.lower().strip()

    statement = select(User).where(User.email == email)
    db_user = db.exec(statement).first()

    if not db_user or user.password != db_user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_token(db_user.id)

    return {
        "access_token": access_token
    }

