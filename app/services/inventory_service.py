from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.inventory import InventoryUpdate, InventoryResponse
from app.utils.security import block_suspended_vendor

def get_inventory_items(
    db: Session,
    current_user: User,
    status_filter: Optional[str] = None
) -> List[dict]:
    query = db.query(Inventory).join(Product)

    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor:
            return []
        query = query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    items = query.order_by(Inventory.inventory_id.asc()).all()

    result = []
    for item in items:
        inv_status = item.status
        if status_filter and status_filter != "All" and inv_status != status_filter:
            continue
        result.append({
            "inventory_id": item.inventory_id,
            "product_id": item.product_id,
            "product_name": item.product.product_name if item.product else None,
            "vendor_id": item.product.vendor_id if item.product else None,
            "vendor_name": item.product.vendor.business_name if (item.product and item.product.vendor) else None,
            "current_stock": item.current_stock,
            "reorder_level": item.reorder_level,
            "warehouse": item.warehouse,
            "status": inv_status,
            "updated_at": item.updated_at
        })
    return result

def get_inventory_by_product_id(
    db: Session,
    product_id: int,
    current_user: User
) -> dict:
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory for product ID {product_id} not found."
        )

    # Authorization check
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != inventory.product.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view inventory for this product."
            )

    return {
        "inventory_id": inventory.inventory_id,
        "product_id": inventory.product_id,
        "product_name": inventory.product.product_name if inventory.product else None,
        "vendor_id": inventory.product.vendor_id if inventory.product else None,
        "vendor_name": inventory.product.vendor.business_name if (inventory.product and inventory.product.vendor) else None,
        "current_stock": inventory.current_stock,
        "reorder_level": inventory.reorder_level,
        "warehouse": inventory.warehouse,
        "status": inventory.status,
        "updated_at": inventory.updated_at
    }

def update_inventory_by_product_id(
    db: Session,
    product_id: int,
    data: InventoryUpdate,
    current_user: User
) -> dict:
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory for product ID {product_id} not found."
        )

    # Item 8: Block suspended vendors
    block_suspended_vendor(current_user)

    # Authorization check
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != inventory.product.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update inventory for this product."
            )

    update_dict = data.model_dump(exclude_unset=True)

    if "current_stock" in update_dict and update_dict["current_stock"] is not None:
        new_stock = update_dict["current_stock"]
        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Stock cannot be negative."
            )
        inventory.current_stock = new_stock
        # Sync product stock
        if inventory.product:
            inventory.product.stock = new_stock

    if "reorder_level" in update_dict and update_dict["reorder_level"] is not None:
        if update_dict["reorder_level"] < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Reorder level cannot be negative."
            )
        inventory.reorder_level = update_dict["reorder_level"]

    if "warehouse" in update_dict and update_dict["warehouse"] is not None:
        inventory.warehouse = update_dict["warehouse"].strip()

    db.commit()
    db.refresh(inventory)

    return {
        "inventory_id": inventory.inventory_id,
        "product_id": inventory.product_id,
        "product_name": inventory.product.product_name if inventory.product else None,
        "vendor_id": inventory.product.vendor_id if inventory.product else None,
        "vendor_name": inventory.product.vendor.business_name if (inventory.product and inventory.product.vendor) else None,
        "current_stock": inventory.current_stock,
        "reorder_level": inventory.reorder_level,
        "warehouse": inventory.warehouse,
        "status": inventory.status,
        "updated_at": inventory.updated_at
    }
