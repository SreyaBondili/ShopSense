from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.VENDOR

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str
    full_name: str
    vendor_id: Optional[int] = None

class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    vendor_id: Optional[int] = None

    model_config = {"from_attributes": True}
