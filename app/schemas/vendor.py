from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.vendor import VendorStatus

class VendorCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=150)
    owner_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=30)
    category: str = Field(..., min_length=2, max_length=80)
    commission_rate: Optional[Decimal] = Field(default=Decimal("10.00"), ge=0, le=100)
    status: Optional[VendorStatus] = VendorStatus.ACTIVE
    user_id: Optional[int] = None

class VendorUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=150)
    owner_name: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=30)
    category: Optional[str] = Field(None, min_length=2, max_length=80)
    commission_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[VendorStatus] = None

class VendorResponse(BaseModel):
    vendor_id: int
    business_name: str
    owner_name: str
    email: str
    phone: str
    category: str
    commission_rate: Decimal
    status: VendorStatus
    created_at: datetime
    user_id: Optional[int] = None

    model_config = {"from_attributes": True}
