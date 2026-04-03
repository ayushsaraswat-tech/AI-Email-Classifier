from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user_model import User
from app.auth import create_access_token
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/test")
def test():
    return {"message": "AUTH WORKING"}


@router.post("/register")
def register(email: str, password: str):
    db = SessionLocal()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = pwd_context.hash(password)

    user = User(email=email, password=hashed)
    db.add(user)
    db.commit()

    return {"message": "User created"}


@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()

    user = db.query(User).filter(User.email == data.email).first()

    # 🔥 DEBUG HERE
    print("RAW PASSWORD:", data.password)
    print("HASHED:", user.password if user else "NO USER FOUND")

    if user:
        print("VERIFY:", pwd_context.verify(data.password, user.password))

    # ❗ ACTUAL CHECK
    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user.email,
        "role": user.role
    })

    return {"access_token": token}