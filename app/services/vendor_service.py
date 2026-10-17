from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.vendor import Vendor, VendorStatus
from app.models.user import User, UserRole
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse
from app.utils.validators import validate_vendor_registration

def create_vendor(db: Session, data: VendorCreate, current_user: User) -> Vendor:
    # 1. Run rigorous vendor registration validation
    payload = data.model_dump()
    errors = validate_vendor_registration(payload)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    # 2. Check for duplicate vendor email
    norm_email = data.email.strip().lower()
    existing = db.query(Vendor).filter(Vendor.email == norm_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vendor with email '{norm_email}' already exists."
        )

    # 3. Determine user_id linkage
    assigned_user_id = None
    if current_user.role == UserRole.ADMIN:
        assigned_user_id = data.user_id
    elif current_user.role == UserRole.VENDOR:
        assigned_user_id = current_user.user_id

    # 4. Create vendor
    vendor = Vendor(
        business_name=data.business_name.strip(),
        owner_name=data.owner_name.strip(),
        email=norm_email,
        phone=data.phone.strip(),
        category=data.category.strip(),
        commission_rate=data.commission_rate if data.commission_rate is not None else 10.00,
        status=data.status or VendorStatus.ACTIVE,
        user_id=assigned_user_id
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

def get_vendors(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    category: Optional[str] = None,
    vendor_status: Optional[str] = None
) -> List[Vendor]:
    query = db.query(Vendor)

    # Role-based restriction: Vendors can only view their own vendor record
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor:
            return []
        query = query.filter(Vendor.vendor_id == current_user.vendor.vendor_id)
    else:
        # Admin filters
        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                (Vendor.business_name.ilike(s)) |
                (Vendor.owner_name.ilike(s)) |
                (Vendor.email.ilike(s))
            )
        if category and category != "All":
            query = query.filter(Vendor.category == category)
        if vendor_status and vendor_status != "All":
            query = query.filter(Vendor.status == vendor_status)

    return query.order_by(Vendor.vendor_id.asc()).all()

def get_vendor_by_id(db: Session, vendor_id: int, current_user: User) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )

    # Authorization check
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this vendor's details."
            )

    return vendor

def update_vendor(db: Session, vendor_id: int, data: VendorUpdate, current_user: User) -> Vendor:
    vendor = get_vendor_by_id(db, vendor_id, current_user)

    # If vendor is updating, they cannot modify status or commission_rate
    if current_user.role == UserRole.VENDOR:
        if data.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendors are not permitted to alter vendor status."
            )
        if data.commission_rate is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendors cannot alter commission rates. Contact Admin."
            )

    update_dict = data.model_dump(exclude_unset=True)

    # Email uniqueness check if changing email
    if "email" in update_dict and update_dict["email"]:
        new_email = update_dict["email"].strip().lower()
        if new_email != vendor.email:
            existing = db.query(Vendor).filter(Vendor.email == new_email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{new_email}' is already in use by another vendor."
                )
            vendor.email = new_email

    for key, val in update_dict.items():
        if key != "email" and hasattr(vendor, key) and val is not None:
            setattr(vendor, key, val)

    db.commit()
    db.refresh(vendor)
    return vendor

def delete_vendor(db: Session, vendor_id: int, current_user: User) -> dict:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete vendors."
        )

    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )

    db.delete(vendor)
    db.commit()
    return {"message": f"Vendor {vendor_id} successfully deleted."}
