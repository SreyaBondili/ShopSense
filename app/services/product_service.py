from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.vendor import Vendor, VendorStatus
from app.models.inventory import Inventory
from app.models.transaction import Transaction
from app.models.user import User, UserRole
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.security import block_suspended_vendor

def create_product(db: Session, data: ProductCreate, current_user: User) -> Product:
    # 1. Determine vendor_id
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your user account is not linked to any active vendor profile."
            )
        target_vendor_id = current_user.vendor.vendor_id
    else:
        # Admin must specify vendor_id
        if not data.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="vendor_id is required for product creation."
            )
        target_vendor_id = data.vendor_id

    # 2. Check vendor exists and is not suspended
    vendor = db.query(Vendor).filter(Vendor.vendor_id == target_vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {target_vendor_id} does not exist."
        )
    if vendor.status == VendorStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add products to a SUSPENDED vendor."
        )

    # 3. Check for duplicate product name under the same vendor
    existing_product = db.query(Product).filter(
        Product.vendor_id == target_vendor_id,
        Product.product_name == data.product_name.strip()
    ).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A product named '{data.product_name.strip()}' already exists in this vendor's catalog."
        )

    # 4. Validate price and stock
    if data.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product price must be greater than zero."
        )
    if data.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Initial product stock cannot be negative."
        )

    # 5. Create product
    product = Product(
        product_name=data.product_name.strip(),
        category=data.category.strip(),
        price=data.price,
        stock=data.stock,
        vendor_id=target_vendor_id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # 5. Automatically create corresponding Inventory record
    inventory = Inventory(
        product_id=product.product_id,
        current_stock=product.stock,
        warehouse="Main Warehouse",
        reorder_level=10
    )
    db.add(inventory)
    db.commit()

    return product

def get_products(
    db: Session,
    current_user: Optional[User] = None,
    vendor_id: Optional[int] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[Product]:
    query = db.query(Product).join(Vendor)

    # Vendor role restriction
    if current_user and current_user.role == UserRole.VENDOR:
        if not current_user.vendor:
            return []
        query = query.filter(Product.vendor_id == current_user.vendor.vendor_id)
    elif vendor_id:
        query = query.filter(Product.vendor_id == vendor_id)

    if category and category != "All":
        query = query.filter(Product.category == category)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (Product.product_name.ilike(s)) |
            (Product.category.ilike(s)) |
            (Vendor.business_name.ilike(s))
        )

    return query.order_by(Product.product_id.asc()).all()

def get_product_by_id(db: Session, product_id: int, current_user: Optional[User] = None) -> Product:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    if current_user and current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != product.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this product."
            )

    return product

def update_product(db: Session, product_id: int, data: ProductUpdate, current_user: User) -> Product:
    # Item 8: Block suspended vendors from editing products
    block_suspended_vendor(current_user)
    product = get_product_by_id(db, product_id, current_user)

    update_dict = data.model_dump(exclude_unset=True)

    if "price" in update_dict and update_dict["price"] is not None:
        if update_dict["price"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Price must be greater than zero."
            )
        product.price = update_dict["price"]

    if "product_name" in update_dict and update_dict["product_name"] is not None:
        product.product_name = update_dict["product_name"].strip()

    if "category" in update_dict and update_dict["category"] is not None:
        product.category = update_dict["category"].strip()

    if "stock" in update_dict and update_dict["stock"] is not None:
        if update_dict["stock"] < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Stock cannot be negative."
            )
        product.stock = update_dict["stock"]
        # Sync with Inventory record
        if product.inventory:
            product.inventory.current_stock = update_dict["stock"]
        else:
            new_inv = Inventory(product_id=product.product_id, current_stock=update_dict["stock"])
            db.add(new_inv)

    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int, current_user: User) -> dict:
    product = get_product_by_id(db, product_id, current_user)

    # Item 2: Protect sales history — refuse delete if transactions exist
    if db.query(Transaction).filter(Transaction.product_id == product_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This product has sales history and cannot be deleted. Set its stock to 0 instead."
        )

    db.delete(product)
    db.commit()
    return {"message": f"Product {product_id} successfully deleted."}
