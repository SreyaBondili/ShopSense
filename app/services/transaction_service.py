from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.transaction import Transaction
from app.models.product import Product
from app.models.vendor import Vendor, VendorStatus
from app.models.inventory import Inventory
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionResponse

def create_transaction(
    db: Session,
    data: TransactionCreate,
    current_user: User
) -> Transaction:
    # 1. Verify quantity > 0
    if data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Transaction quantity must be strictly greater than zero."
        )

    # 2. Verify product exists
    product = db.query(Product).filter(Product.product_id == data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {data.product_id} not found."
        )

    # 3. Verify vendor exists and is active
    vendor = db.query(Vendor).filter(Vendor.vendor_id == product.vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Associated vendor with ID {product.vendor_id} does not exist."
        )
    if vendor.status != VendorStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vendor '{vendor.business_name}' is currently {vendor.status.value}. Cannot execute transaction."
        )

    # If VENDOR user is creating transaction, ensure it belongs to their vendor
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != vendor.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendors may only record transactions for their own catalog items."
            )

    # 4. Fetch Inventory and check available stock (with row-level lock to prevent overselling)
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product.product_id
    ).with_for_update().first()
    if not inventory:
        # Create inventory record if missing
        inventory = Inventory(product_id=product.product_id, current_stock=product.stock)
        db.add(inventory)
        db.flush()

    if inventory.current_stock < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient inventory for '{product.product_name}'. Requested: {data.quantity}, Available: {inventory.current_stock}"
        )

    # 5. Safely deduct inventory and product stock
    inventory.current_stock -= data.quantity
    product.stock = inventory.current_stock

    # 6. Compute total transaction amount
    total_amount = round(float(product.price) * data.quantity, 2)

    # 7. Create transaction record
    new_transaction = Transaction(
        product_id=product.product_id,
        vendor_id=vendor.vendor_id,
        user_id=current_user.user_id if current_user else None,
        quantity=data.quantity,
        amount=total_amount,
        transaction_date=datetime.now()
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

def get_transactions(
    db: Session,
    current_user: User,
    vendor_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> List[dict]:
    query = db.query(Transaction).join(Product).join(Vendor)

    # Role restriction: Vendor sees their shop sales, Customer sees ONLY their personal orders, Admin sees all
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor:
            return []
        query = query.filter(Transaction.vendor_id == current_user.vendor.vendor_id)
    elif current_user.role == UserRole.CUSTOMER:
        query = query.filter(Transaction.user_id == current_user.user_id)
    elif vendor_id:
        query = query.filter(Transaction.vendor_id == vendor_id)

    if product_id:
        query = query.filter(Transaction.product_id == product_id)

    records = query.order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc()).all()

    result = []
    for r in records:
        result.append({
            "transaction_id": r.transaction_id,
            "product_id": r.product_id,
            "product_name": r.product.product_name if r.product else None,
            "vendor_id": r.vendor_id,
            "vendor_name": r.vendor.business_name if r.vendor else None,
            "user_id": r.user_id,
            "quantity": r.quantity,
            "amount": r.amount,
            "transaction_date": r.transaction_date
        })
    return result

def get_transaction_by_id(
    db: Session,
    transaction_id: int,
    current_user: User
) -> dict:
    t = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found."
        )

    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != t.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this transaction."
            )
    elif current_user.role == UserRole.CUSTOMER:
        if t.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this order."
            )

    return {
        "transaction_id": t.transaction_id,
        "product_id": t.product_id,
        "product_name": t.product.product_name if t.product else None,
        "vendor_id": t.vendor_id,
        "vendor_name": t.vendor.business_name if t.vendor else None,
        "quantity": t.quantity,
        "amount": t.amount,
        "transaction_date": t.transaction_date
    }
