from fastapi import APIRouter, Depends, Query, HTTPException, status
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
from app.utils.security import get_current_active_user, require_admin, require_roles
from app.models.user import User, UserRole
from app.models.vendor import Vendor

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/revenue")
def get_advanced_revenue_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Milestone 3 Module 2: Advanced revenue analysis, GMV, growth %, vendor/product rankings, and profit/loss (Admin only)."""
    return revenue_service.get_advanced_revenue_analysis(db, current_user, vendor_id)

@router.get("/vendor-revenue")
def get_vendor_revenue_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("VENDOR", "ADMIN"))
):
    """Milestone 3 Module 2: Vendor-scoped revenue analysis, GMV, growth %, and product rankings for authenticated vendor."""
    vendor_id = current_user.vendor.vendor_id if current_user.vendor else None
    return revenue_service.get_advanced_revenue_analysis(db, current_user, vendor_id)

@router.get("/vendor-recommendations")
def get_vendor_recommendation_metrics(
    k: int = Query(5, description="Top-K cutoff for recommendation analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("VENDOR", "ADMIN"))
):
    """
    Vendor-scoped recommendation analytics: evaluates collaborative filtering reach,
    catalog coverage %, and recommendation impressions for the authenticated vendor's products.
    Secured by backend authentication token.
    """
    from app.services import recommendation_service
    if current_user.role == UserRole.VENDOR:
        vendor = current_user.vendor
        if not vendor:
            vendor = db.query(Vendor).filter(Vendor.user_id == current_user.user_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found for authenticated user.")
        vendor_id = vendor.vendor_id
    else:
        # Admin inspecting vendor recommendations
        vendor = db.query(Vendor).first()
        vendor_id = vendor.vendor_id if vendor else 1

    return recommendation_service.evaluate_vendor_recommendations(db, vendor_id=vendor_id, k=k)

@router.get("/mlflow-status")
def get_mlflow_tracking_status(
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Milestone 3 Module 3: Retrieve MLflow model tracking, metrics, and registered models (Admin only)."""
    return mlflow_service.get_mlflow_status()

@router.post("/mlflow-retrain")
def retrain_mlflow_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Milestone 3 Module 3: Trigger model retraining and log run to MLflow Model Registry (Admin only)."""
    return mlflow_service.train_and_log_inventory_model(db, run_notes=f"Retrained by {current_user.email}")

@router.get("/summary", response_model=MarketplaceSummary)
def get_analytics_summary(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Get high-level summary KPIs (Total Revenue, Transactions, Quantity Sold, ATV) for Admin or Vendor."""
    return analytics_service.get_summary(db, current_user, vendor_id)

@router.get("/customers")
def get_customer_behavior_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Module 2.A: Customer purchasing behavior, lifetime spending, and frequency (Admin only)."""
    return customer_analytics_service.get_customer_behavior_analytics(db, current_user)

@router.get("/segments")
def get_customer_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Module 2.B: Customer Segmentation using K-Means with Silhouette Score evaluation (Admin only)."""
    return customer_analytics_service.get_customer_segmentation(db, current_user)

@router.get("/vendor-performance", response_model=List[VendorPerformanceItem])
def get_vendor_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Get vendor performance metrics with revenue, transaction counts, and quantity sold (Admin only)."""
    return analytics_service.get_vendor_performance(db, current_user)

@router.get("/product-performance", response_model=List[ProductPerformanceItem])
def get_product_performance_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Get product performance analytics including units sold, revenue, and stock status."""
    return analytics_service.get_product_performance(db, current_user, vendor_id)

@router.get("/revenue-trend", response_model=List[RevenueTrendItem])
def get_revenue_trend_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Get time-series revenue and sales trends aggregated by date."""
    return analytics_service.get_revenue_trend(db, current_user, vendor_id)

@router.get("/category-performance", response_model=List[CategoryPerformanceItem])
def get_category_performance_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Get category-level sales breakdown."""
    return analytics_service.get_category_performance(db, current_user, vendor_id)

@router.get("/recommendation-quality")
def get_recommendation_quality_metrics(
    k: int = Query(5, description="Top-K cutoff for leave-last-purchase-out offline evaluation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """
    Task 2 & Mentor Milestone 3: Rigorous offline evaluation using Leave-Last-Purchase-Out.
    Computes Hit-Rate@K, Precision@K, and Recommendation Relevance % (Admin only).
    """
    from app.services import recommendation_service
    return recommendation_service.evaluate_recommendations_offline_leave_last_out(db, k=k)
