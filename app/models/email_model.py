from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)

    category = Column(String)
    intent = Column(String)
    priority = Column(String)
    sentiment = Column(String)

    draft_response = Column(Text)

    status = Column(String, default="PENDING")
    approver = Column(String, nullable=True)
    ai_explanation = Column(Text, nullable=True)