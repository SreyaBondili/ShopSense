from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.services import recommendation_service
from app.utils.security import get_current_active_user, require_roles
from app.models.user import User, UserRole
from app.models.vendor import Vendor

router = APIRouter(tags=["Recommendations"])

@router.get("/api/recommendations")
def get_user_recommendations(
    limit: int = Query(5, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Module 3.A: Personalized product recommendations using item-based collaborative filtering.
    """
    return recommendation_service.get_recommendations_for_user(db, current_user.user_id, limit=limit)

@router.get("/api/recommendations/evaluation")
def get_recommendation_evaluation(
    k: int = Query(5, description="Top-K evaluation cutoff"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """
    Module 3.B: Recommendation Engine Evaluation metrics: Precision@K, Recall@K, Coverage (Admin only).
    """
    return recommendation_service.evaluate_recommendations(db, k=k)

@router.get("/api/recommendations/vendor")
def get_vendor_recommendation_evaluation(
    k: int = Query(5, description="Top-K evaluation cutoff"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("VENDOR", "ADMIN"))
):
    """
    Vendor-specific recommendation analytics: evaluates collaborative filtering reach,
    catalog coverage %, and recommendation impressions for the authenticated vendor's products.
    """
    if current_user.role == UserRole.VENDOR:
        vendor = current_user.vendor
        if not vendor:
            vendor = db.query(Vendor).filter(Vendor.user_id == current_user.user_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found for authenticated user.")
        vendor_id = vendor.vendor_id
    else:
        vendor = db.query(Vendor).first()
        vendor_id = vendor.vendor_id if vendor else 1

    return recommendation_service.evaluate_vendor_recommendations(db, vendor_id=vendor_id, k=k)

@router.get("/api/recommend/{user_id}")
def get_recommendations_by_user_id(
    user_id: int,
    limit: int = Query(5, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Task 2 & Mentor Spec: Personalized product recommendations for a specific user ID.
    Enforces object-level access control:
    - Customer can ONLY view their own recommendations (403 for another user's ID).
    - Vendor accounts cannot view customer recommendations (403).
    - Admin accounts can view recommendations for any user ID.
    """
    if current_user.role == UserRole.CUSTOMER and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: customer #{current_user.user_id} cannot access recommendations for user #{user_id}."
        )
    if current_user.role == UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: vendor accounts cannot access customer recommendation profiles."
        )

    return recommendation_service.get_recommendations_for_user(db, user_id, limit=limit)

@router.get("/api/recommend/segment/{segment}")
def get_segment_recommendations(
    segment: str,
    limit: int = Query(5, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Task 2: Cohort / Segment-level product recommendations
    (e.g., 'High Spenders', 'Frequent Buyers', 'Dormant Users', 'Occasional Buyers').
    """
    return recommendation_service.get_recommendations_for_segment(db, segment, limit=limit)
