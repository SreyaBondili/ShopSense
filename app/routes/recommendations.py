from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.services import recommendation_service
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("")
def get_user_recommendations(
    limit: int = Query(5, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Module 3.A: Personalized product recommendations using Cosine Similarity.
    Recommends top products tailored to customer preferences, excluding out-of-stock items.
    """
    return recommendation_service.get_recommendations_for_user(db, current_user.user_id, limit=limit)

@router.get("/evaluation")
def get_recommendation_evaluation(
    k: int = Query(5, description="Top-K evaluation cutoff"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Module 3.B: Recommendation Engine Evaluation metrics: Precision@K, Recall@K, Coverage, Relevance >= 75%.
    """
    return recommendation_service.evaluate_recommendations(db, k=k)
