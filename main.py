import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, String, Integer, Boolean, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auth.db")
JWT_SECRET = os.getenv("JWT_SECRET", "")
if len(JWT_SECRET) < 32 or JWT_SECRET.startswith("replace-"):
    raise RuntimeError("Set JWT_SECRET to a random value of at least 32 characters in .env")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

Base.metadata.create_all(engine)
app = FastAPI(title="Login Signup API")
origins = [x.strip() for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])
hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def token_for(user):
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=1)}, JWT_SECRET, algorithm="HS256")

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(db_session)):
    error = HTTPException(status_code=401, detail="Invalid or expired token")
    if not creds:
        raise error
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
        user = db.get(User, int(payload["sub"]))
    except Exception:
        raise error
    if not user or not user.is_active:
        raise error
    return user

@app.get("/")
def home(): return {"message": "API is running"}
@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/auth/signup", response_model=AuthOut, status_code=201)
def signup(data: SignupIn, db: Session = Depends(db_session)):
    if len(data.name.strip()) < 2:
        raise HTTPException(400, "Name must be at least 2 characters")
    if len(data.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    email = str(data.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(name=data.name.strip(), email=email, password_hash=hasher.hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": token_for(user), "user": user}

@app.post("/auth/login", response_model=AuthOut)
def login(data: LoginIn, db: Session = Depends(db_session)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if not user or not hasher.verify(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")
    return {"access_token": token_for(user), "user": user}

@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
