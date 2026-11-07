from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.schemas.analytics import (
    MarketplaceSummary,
    VendorPerformanceItem,
    ProductPerformanceItem,
    RevenueTrendItem,
    CategoryPerformanceItem,
)
from app.services import analytics_service, customer_analytics_service, revenue_service, mlflow_service
from app.utils.security import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/revenue")
def get_advanced_revenue_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Milestone 3 Module 2: Advanced revenue analysis, GMV, growth %, vendor/product rankings, and profit/loss."""
    return revenue_service.get_advanced_revenue_analysis(db, current_user, vendor_id)

@router.get("/mlflow-status")
def get_mlflow_tracking_status(
    current_user: User = Depends(get_current_active_user)
):
    """Milestone 3 Module 3: Retrieve MLflow model tracking, metrics, and registered models."""
    return mlflow_service.get_mlflow_status()

@router.post("/mlflow-retrain")
def retrain_mlflow_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Milestone 3 Module 3: Trigger model retraining and log run to MLflow Model Registry."""
    return mlflow_service.train_and_log_inventory_model(db, run_notes=f"Retrained by {current_user.email}")

@router.get("/summary", response_model=MarketplaceSummary)
def get_analytics_summary(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get high-level summary KPIs (Total Revenue, Transactions, Quantity Sold, ATV)."""
    return analytics_service.get_summary(db, current_user, vendor_id)

@router.get("/customers")
def get_customer_behavior_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 2.A: Customer purchasing behavior, lifetime spending, and frequency."""
    return customer_analytics_service.get_customer_behavior_analytics(db, current_user)

@router.get("/segments")
def get_customer_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Module 2.B: Customer Segmentation using K-Means with Silhouette Score evaluation."""
    return customer_analytics_service.get_customer_segmentation(db, current_user)

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
