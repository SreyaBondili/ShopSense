from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse
from app.services import vendor_service
from app.utils.security import get_current_active_user, require_admin, require_roles
from app.models.user import User

router = APIRouter(prefix="/api/vendors", tags=["Vendors"])

@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(
    payload: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Onboard/register a new vendor with validation (Admin or Vendor only)."""
    return vendor_service.create_vendor(db, payload, current_user)

@router.get("", response_model=List[VendorResponse])
def get_vendors(
    search: Optional[str] = Query(None, description="Search by business, owner, or email"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, ACTIVE, SUSPENDED)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Retrieve vendors (Admins view all; Vendors view own). CUSTOMER rejected with 403."""
    return vendor_service.get_vendors(db, current_user, search, category, status_filter)

@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Get single vendor details by ID (Admin or own Vendor only)."""
    return vendor_service.get_vendor_by_id(db, vendor_id, current_user)

@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: int,
    payload: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "VENDOR"))
):
    """Update vendor information or status (status update restricted to Admin)."""
    return vendor_service.update_vendor(db, vendor_id, payload, current_user)

@router.delete("/{vendor_id}")
def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Admin-only deletion of a vendor."""
    return vendor_service.delete_vendor(db, vendor_id, current_user)
