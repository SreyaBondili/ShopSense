from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.inventory import InventoryUpdate, InventoryResponse
from app.services import inventory_service
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryResponse])
def get_inventory(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (IN STOCK, LOW STOCK, OUT OF STOCK)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View inventory levels and warehouse status with visual status categorization."""
    return inventory_service.get_inventory_items(db, current_user, status_filter)

@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory_for_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve detailed inventory tracking for a single product."""
    return inventory_service.get_inventory_by_product_id(db, product_id, current_user)

@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update stock counts, reorder levels, or warehouse location."""
    return inventory_service.update_inventory_by_product_id(db, product_id, payload, current_user)
