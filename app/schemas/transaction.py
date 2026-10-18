from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TransactionCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    vendor_id: Optional[int] = None

class TransactionResponse(BaseModel):
    transaction_id: int
    product_id: int
    product_name: Optional[str] = None
    vendor_id: int
    vendor_name: Optional[str] = None
    user_id: Optional[int] = None
    quantity: int
    amount: Decimal
    transaction_date: datetime

    model_config = {"from_attributes": True}
