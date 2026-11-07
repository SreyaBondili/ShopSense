from app.routes.auth import router as auth_router
from app.routes.vendors import router as vendors_router
from app.routes.products import router as products_router
from app.routes.inventory import router as inventory_router
from app.routes.transactions import router as transactions_router
from app.routes.analytics import router as analytics_router
from app.routes.recommendations import router as recommendations_router
from app.routes.reports import router as reports_router
from app.routes.scheduler import router as scheduler_router

__all__ = [
    "auth_router",
    "vendors_router",
    "products_router",
    "inventory_router",
    "transactions_router",
    "analytics_router",
    "recommendations_router",
    "reports_router",
    "scheduler_router",
]
