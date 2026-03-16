from pydantic import BaseModel, EmailStr


class EmailInput(BaseModel):
    sender: EmailStr
    subject: str
    body: str