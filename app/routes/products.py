from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services import product_service
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new product to catalog and initialize inventory."""
    p = product_service.create_product(db, payload, current_user)
    return ProductResponse(
        product_id=p.product_id,
        product_name=p.product_name,
        category=p.category,
        price=p.price,
        stock=p.stock,
        vendor_id=p.vendor_id,
        created_at=p.created_at,
        vendor_name=p.vendor.business_name if p.vendor else None
    )

@router.get("", response_model=List[ProductResponse])
def get_products(
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name, category or vendor"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List products with optional search and category filters."""
    products = product_service.get_products(db, current_user, vendor_id, category, search)
    return [
        ProductResponse(
            product_id=p.product_id,
            product_name=p.product_name,
            category=p.category,
            price=p.price,
            stock=p.stock,
            vendor_id=p.vendor_id,
            created_at=p.created_at,
            vendor_name=p.vendor.business_name if p.vendor else None
        ) for p in products
    ]

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get single product details."""
    p = product_service.get_product_by_id(db, product_id, current_user)
    return ProductResponse(
        product_id=p.product_id,
        product_name=p.product_name,
        category=p.category,
        price=p.price,
        stock=p.stock,
        vendor_id=p.vendor_id,
        created_at=p.created_at,
        vendor_name=p.vendor.business_name if p.vendor else None
    )

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update product and synchronize stock with inventory."""
    p = product_service.update_product(db, product_id, payload, current_user)
    return ProductResponse(
        product_id=p.product_id,
        product_name=p.product_name,
        category=p.category,
        price=p.price,
        stock=p.stock,
        vendor_id=p.vendor_id,
        created_at=p.created_at,
        vendor_name=p.vendor.business_name if p.vendor else None
    )

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a product from the catalog."""
    return product_service.delete_product(db, product_id, current_user)
