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
class RegisterRequest(BaseModel):
    email: str
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/test")
def test():
    return {"message": "AUTH WORKING"}




@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not pwd_context.verify(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({
            "sub": user.email,
            "role": user.role
        })

        return {"access_token": token}

    finally:
        db.close()


@router.post("/register")
def register(data: RegisterRequest):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed = pwd_context.hash(data.password)

        user = User(email=data.email, password=hashed, role="user")
        db.add(user)
        db.commit()

        return {"message": "User created"}

    finally:
        db.close()