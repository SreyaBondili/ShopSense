from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.VENDOR
    admin_secret: Optional[str] = None
    phone: Optional[str] = None
    business_name: Optional[str] = None
    category: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, v: str) -> str:
        """Bcrypt silently truncates at 72 bytes; reject passwords that exceed this."""
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long")
        return v

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
