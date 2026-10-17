from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services import transaction_service
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def record_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Execute a marketplace sale transaction with atomic inventory reduction."""
    t = transaction_service.create_transaction(db, payload, current_user)
    return TransactionResponse(
        transaction_id=t.transaction_id,
        product_id=t.product_id,
        product_name=t.product.product_name if t.product else None,
        vendor_id=t.vendor_id,
        vendor_name=t.vendor.business_name if t.vendor else None,
        quantity=t.quantity,
        amount=t.amount,
        transaction_date=t.transaction_date
    )

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List historical transaction log (scoped to role: Admin sees all, Vendor sees own)."""
    return transaction_service.get_transactions(db, current_user, vendor_id, product_id)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get single transaction record by ID."""
    return transaction_service.get_transaction_by_id(db, transaction_id, current_user)
