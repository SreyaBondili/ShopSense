from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductCreate(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=150)
    category: str = Field(..., min_length=2, max_length=80)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    vendor_id: Optional[int] = None

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=2, max_length=150)
    category: Optional[str] = Field(None, min_length=2, max_length=80)
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)

class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: Decimal
    stock: int
    vendor_id: int
    created_at: datetime
    vendor_name: Optional[str] = None

    model_config = {"from_attributes": True}
