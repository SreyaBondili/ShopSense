from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.schemas.inventory import InventoryUpdate, InventoryResponse
from app.services import inventory_service, replenishment_service, forecasting_service
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

@router.get("/alerts")
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 1.E: Low-Stock and Out-of-Stock alert system with shortage calculations."""
    return replenishment_service.get_low_stock_alerts(db, current_user)

@router.get("/turnover")
def get_turnover_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 1.C: Inventory Turnover = COGS / Average Inventory Value."""
    return replenishment_service.get_inventory_turnover(db, current_user)

@router.get("/forecast")
def get_inventory_demand_forecast(
    product_id: Optional[int] = Query(None, description="Optional filter by product ID"),
    horizon: int = Query(14, description="Forecast horizon in days (e.g. 7, 14, 30)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 1.D: Random Forest demand forecasting with held-out chronological accuracy."""
    return forecasting_service.generate_demand_forecast(db, current_user, product_id, horizon)

@router.get("/replenishment")
def get_replenishment_suggestions(
    lead_time_days: int = Query(5, description="Supplier lead time in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 1.F: Suggested Reorder Quantity = Target Stock - Current Stock."""
    return replenishment_service.get_replenishment_recommendations(db, current_user, lead_time_days)

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
