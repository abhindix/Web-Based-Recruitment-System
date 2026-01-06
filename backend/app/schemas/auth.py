from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
