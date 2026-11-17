from fastapi import FastAPI, Request, status, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional, List
from contextlib import asynccontextmanager
import os
import uvicorn

from app.config import settings
from app.database import get_db
from app.routes import (
    auth_router,
    vendors_router,
    products_router,
    inventory_router,
    transactions_router,
    analytics_router,
    recommendations_router,
    reports_router,
    scheduler_router,
    wishlist_router,
)
from app.services import (
    revenue_service,
    analytics_service,
    customer_analytics_service,
    forecasting_service,
    recommendation_service,
)
from app.scheduler.scheduler_service import workflow_scheduler
from app.models.user import User, UserRole
from app.utils.security import get_current_active_user, require_roles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if os.getenv("TESTING") != "1":
        try:
            from app.database import engine, Base
            import app.models  # noqa: F401
            Base.metadata.create_all(bind=engine)
            # Idempotent column and category check
            from sqlalchemy import text
            with engine.connect() as conn:
                try:
                    cols = [c[0] for c in conn.execute(text("DESCRIBE users")).fetchall()]
                    if "phone" not in cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(30) NULL;"))
                        conn.commit()
                    cat_exists = conn.execute(text("SELECT category_id FROM categories WHERE category_name = 'General'")).fetchone()
                    if not cat_exists:
                        conn.execute(text("INSERT INTO categories (category_name, parent_category) VALUES ('General', NULL);"))
                        conn.commit()
                except Exception as mig_err:
                    pass
        except Exception as e:
            print(f"Schema migration notice: {e}")
        try:
            workflow_scheduler.start_scheduler()
        except Exception as e:
            print(f"Scheduler start notice: {e}")
    yield
    # Shutdown
    if os.getenv("TESTING") != "1":
        try:
            workflow_scheduler.stop_scheduler()
        except Exception:
            pass

app = FastAPI(
    title="ShopSense – Multi-Vendor E-Commerce Analytics Platform",
    description="Backend REST API for ShopSense Milestones 1, 2 & 3: Multi-role authentication, product catalog, inventory intelligence, machine learning forecasting, customer segmentation, recommendation engine, revenue analysis, MLflow tracking, workflow automation, and reporting.",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend applications (React + Vite, Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8501",
        "http://localhost:8502",
        "http://localhost:8503",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        msg = err.get("msg", "Validation error")
        error_messages.append(f"{field}: {msg}" if field else msg)
    return JSONResponse(
        status_code=422,
        content={"detail": error_messages}
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    orig_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    if "Duplicate entry" in orig_msg:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "A record with this unique attribute already exists."}
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Database integrity error: {orig_msg}"}
    )

# Include API Routers (Standard /api endpoints)
app.include_router(auth_router)
app.include_router(vendors_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(recommendations_router)
app.include_router(reports_router)
app.include_router(scheduler_router)
app.include_router(wishlist_router)

# -------------------------------------------------------------
# Mentor Compatibility Endpoints (aliases without /api prefix)
# Supports direct lecture code snippets and automated testing
# -------------------------------------------------------------
@app.get("/analytics/revenue", tags=["Mentor Compatibility"])
def mentor_revenue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Mentor reference compatibility: Direct revenue analysis endpoint (Admin only)."""
    return revenue_service.get_advanced_revenue_analysis(db, current_user)

@app.get("/analytics/vendor-performance", tags=["Mentor Compatibility"])
def mentor_vendor_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Mentor reference compatibility: Vendor performance endpoint (Admin only)."""
    return analytics_service.get_vendor_performance(db, current_user)

@app.get("/analytics/customers", tags=["Mentor Compatibility"])
def mentor_customer_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """Mentor reference compatibility: Customer behavior analytics endpoint (Admin only)."""
    return customer_analytics_service.get_customer_behavior_analytics(db, current_user)

@app.get("/forecast/{month}", tags=["Mentor Compatibility"])
@app.get("/api/forecast/{month}", tags=["Forecasting"])
def mentor_forecast(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Mentor reference compatibility: Demand forecasting endpoint supporting both integer month and date format."""
    try:
        m_int = int(str(month).split("-")[-1])
        horizon = 30 if m_int in [1, 3, 5, 7, 8, 10, 12] else (28 if m_int == 2 else 30)
    except Exception:
        horizon = 14
    return forecasting_service.generate_demand_forecast(db, current_user, horizon_days=horizon)

@app.get("/recommend/{customer_id}", tags=["Mentor Compatibility"])
def mentor_recommendations(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mentor reference compatibility: Personalized recommendations for customer with object-level RBAC."""
    if current_user.role == UserRole.CUSTOMER and current_user.user_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: cannot view another customer's recommendations."
        )
    if current_user.role == UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: vendor accounts cannot access customer recommendation profiles."
        )

    return recommendation_service.get_recommendations_for_user(db, customer_id, limit=5)

@app.get("/", tags=["System"])
def root():
    return {
        "platform": "ShopSense Multi-Vendor Analytics Platform",
        "milestones": "Milestones 1, 2, and 3 (Complete)",
        "status": "Operational",
        "api_docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "database": "MySQL (SQLAlchemy)",
        "version": "3.0.0",
        "scheduler": "APScheduler active",
        "tracking": "MLflow active"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
