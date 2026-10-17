from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import uvicorn
from app.config import settings
from app.routes import (
    auth_router,
    vendors_router,
    products_router,
    inventory_router,
    transactions_router,
    analytics_router,
)

app = FastAPI(
    title="ShopSense – Multi-Vendor E-Commerce Analytics Platform",
    description="Backend REST API for ShopSense Milestone 1: Vendor onboarding, product catalog, inventory tracking, sales transactions, and marketplace analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend applications (e.g. Streamlit dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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

# Include API Routers
app.include_router(auth_router)
app.include_router(vendors_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(transactions_router)
app.include_router(analytics_router)

@app.get("/", tags=["System"])
def root():
    return {
        "platform": "ShopSense Multi-Vendor Analytics Platform",
        "milestone": "Milestone 1 (Weeks 1-2)",
        "status": "Operational",
        "api_docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "database": "MySQL (SQLAlchemy)",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
