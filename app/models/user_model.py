from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)

    role = Column(String, default="user")  # admin/user

    full_name = Column(String, nullable=True)
    signature_name = Column(String, nullable=True)
    company_signature = Column(String, nullable=True)