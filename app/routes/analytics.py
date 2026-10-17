from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.analytics import (
    MarketplaceSummary,
    VendorPerformanceItem,
    ProductPerformanceItem,
    RevenueTrendItem,
    CategoryPerformanceItem,
)
from app.services import analytics_service
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary", response_model=MarketplaceSummary)
def get_analytics_summary(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get high-level summary KPIs (Total Revenue, Transactions, Quantity Sold, ATV)."""
    return analytics_service.get_summary(db, current_user, vendor_id)

@router.get("/vendor-performance", response_model=List[VendorPerformanceItem])
def get_vendor_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get vendor performance metrics with revenue, transaction counts, and quantity sold."""
    return analytics_service.get_vendor_performance(db, current_user)

@router.get("/product-performance", response_model=List[ProductPerformanceItem])
def get_product_performance_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get product performance analytics including units sold, revenue, and stock status."""
    return analytics_service.get_product_performance(db, current_user, vendor_id)

@router.get("/revenue-trend", response_model=List[RevenueTrendItem])
def get_revenue_trend_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time-series revenue and sales trends aggregated by date."""
    return analytics_service.get_revenue_trend(db, current_user, vendor_id)

@router.get("/category-performance", response_model=List[CategoryPerformanceItem])
def get_category_performance_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get category-level sales breakdown."""
    return analytics_service.get_category_performance(db, current_user, vendor_id)
