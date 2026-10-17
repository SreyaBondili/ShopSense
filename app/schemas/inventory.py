from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    warehouse: Optional[str] = Field(None, min_length=2, max_length=100)

class InventoryResponse(BaseModel):
    inventory_id: int
    product_id: int
    product_name: Optional[str] = None
    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None
    current_stock: int
    reorder_level: int
    warehouse: str
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}
