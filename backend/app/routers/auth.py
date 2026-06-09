from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import secrets

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

# Simple token store — in production use JWT
active_tokens = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_hex(32)


# ── POST /auth/register ──────────────────────────────────
@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    existing = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email exists
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username   = user_data.username,
        email      = user_data.email,
        password   = hash_password(user_data.password),
        role       = user_data.role,
        created_at = datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message"  : "User created successfully",
        "username" : user.username,
        "role"     : user.role
    }


# ── POST /auth/login ─────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == login_data.username
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user.password != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate token
    token = generate_token()
    active_tokens[token] = {
        "username": user.username,
        "role"    : user.role,
        "expires" : datetime.utcnow() + timedelta(hours=24)
    }

    return TokenResponse(
        access_token = token,
        token_type   = "bearer",
        username     = user.username,
        role         = user.role
    )


# ── POST /auth/verify ────────────────────────────────────
@router.post("/verify")
def verify_token(token: str, db: Session = Depends(get_db)):
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    token_data = active_tokens[token]
    if datetime.utcnow() > token_data["expires"]:
        del active_tokens[token]
        raise HTTPException(status_code=401, detail="Token expired")

    return {
        "valid"   : True,
        "username": token_data["username"],
        "role"    : token_data["role"]
    }


# ── POST /auth/logout ────────────────────────────────────
@router.post("/logout")
def logout(token: str):
    if token in active_tokens:
        del active_tokens[token]
    return {"message": "Logged out successfully"}


# ── GET /auth/users ──────────────────────────────────────
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"username": u.username, "email": u.email, "role": u.role} for u in users]