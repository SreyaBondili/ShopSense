"""Wishlist API routes — Task 10 Schema Alignment.

RBAC:
  POST   /api/wishlist/{product_id}  — CUSTOMER (own wishlist) or ADMIN
  GET    /api/wishlist                — CUSTOMER (own wishlist) or ADMIN
  DELETE /api/wishlist/{product_id}  — CUSTOMER (own wishlist) or ADMIN
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime, timezone

from app.database import get_db
from app.utils.security import require_roles
from app.models.wishlist import CustomerWishlist
from app.models.product import Product

router = APIRouter(prefix="/api/wishlist", tags=["Wishlist"])

def _extract_user_id(user) -> int:
    if isinstance(user, dict):
        return int(user.get("user_id") or user.get("id") or user.get("sub", 0))
    return int(getattr(user, "user_id", getattr(user, "id", 0)))

@router.post("/{product_id}", summary="Add product to wishlist")
def add_to_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    """Add a product to the authenticated customer's wishlist (idempotent)."""
    user_id = _extract_user_id(current_user)

    # Verify product exists
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")

    # Idempotent: skip if already in wishlist
    existing = db.query(CustomerWishlist).filter(
        and_(CustomerWishlist.user_id == user_id, CustomerWishlist.product_id == product_id)
    ).first()
    if existing:
        return {
            "status": "already_in_wishlist",
            "wishlist_id": existing.wishlist_id,
            "user_id": user_id,
            "product_id": product_id,
            "product_name": product.product_name,
            "added_at": existing.added_at.isoformat() if existing.added_at else None
        }

    entry = CustomerWishlist(user_id=user_id, product_id=product_id, added_at=datetime.now(timezone.utc))
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {
        "status": "added",
        "wishlist_id": entry.wishlist_id,
        "user_id": user_id,
        "product_id": product_id,
        "product_name": product.product_name,
        "added_at": entry.added_at.isoformat() if entry.added_at else None
    }

@router.get("", summary="Get wishlist")
def get_wishlist(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    """Retrieve the authenticated customer's wishlist with product details."""
    user_id = _extract_user_id(current_user)
    entries = db.query(CustomerWishlist).filter(CustomerWishlist.user_id == user_id).all()

    items = []
    for e in entries:
        product = db.query(Product).filter(Product.product_id == e.product_id).first()
        items.append({
            "wishlist_id": e.wishlist_id,
            "product_id": e.product_id,
            "product_name": product.product_name if product else "Unknown",
            "product_price": float(product.price) if product else 0.0,
            "category": product.category if product else None,
            "added_at": e.added_at.isoformat() if e.added_at else None
        })

    return {
        "status": "success",
        "user_id": user_id,
        "wishlist_count": len(items),
        "wishlist": items
    }

@router.delete("/{product_id}", summary="Remove product from wishlist")
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    """Remove a product from the authenticated customer's wishlist."""
    user_id = _extract_user_id(current_user)

    entry = db.query(CustomerWishlist).filter(
        and_(CustomerWishlist.user_id == user_id, CustomerWishlist.product_id == product_id)
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not in your wishlist.")

    db.delete(entry)
    db.commit()
    return {
        "status": "removed",
        "user_id": user_id,
        "product_id": product_id
    }
