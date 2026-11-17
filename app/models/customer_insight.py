"""Customer Insight Profiles table — Task 10 Schema Alignment."""
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class CustomerInsightProfile(Base):
    __tablename__ = "customer_insight_profiles"

    insight_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    segment_name = Column(String(100), nullable=True)
    total_spent = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    aov = Column(Float, default=0.0)        # Average Order Value
    recency_days = Column(Integer, default=0)
    is_frequent = Column(Boolean, default=False)
    preferred_category = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
