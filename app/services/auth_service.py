from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.config import settings
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.validators import validate_email_format, validate_owner_name, validate_phone_number

def register_user(db: Session, request: UserRegisterRequest) -> UserResponse:
    # 0. Block public admin registration unless authorized with Admin Security Passcode
    if request.role == UserRole.ADMIN:
        valid_secret = getattr(settings, "ADMIN_REGISTRATION_SECRET", "").strip()
        if not valid_secret or not request.admin_secret or request.admin_secret.strip() != valid_secret:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin accounts cannot be created through public registration without a valid Admin Security Passcode."
            )

    # 1. Validate email format
    is_valid_email, norm_email = validate_email_format(request.email)
    if not is_valid_email:
        raise HTTPException(
            status_code=422,
            detail=norm_email
        )

    # 2. Check duplicate email in users table
    existing_user = db.query(User).filter(User.email == norm_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{norm_email}' is already registered."
        )

    # 3. Validate name
    is_valid_name, name_msg = validate_owner_name(request.full_name)
    if not is_valid_name:
        raise HTTPException(
            status_code=422,
            detail=name_msg
        )

    # 4. Hash password
    hashed_pw = hash_password(request.password)

    # 5. Validate phone number (mandatory for Customer)
    user_phone = None
    if request.role == UserRole.CUSTOMER:
        if not request.phone or not request.phone.strip():
            raise HTTPException(
                status_code=422,
                detail="Phone number is required for customer registration"
            )
        is_valid_phone, phone_msg = validate_phone_number(request.phone.strip())
        if not is_valid_phone:
            raise HTTPException(
                status_code=422,
                detail=phone_msg
            )
        user_phone = phone_msg
    elif request.phone and request.phone.strip():
        is_valid_phone, phone_msg = validate_phone_number(request.phone.strip())
        if is_valid_phone:
            user_phone = phone_msg

    # 6. Create user
    new_user = User(
        full_name=request.full_name.strip(),
        email=norm_email,
        password_hash=hashed_pw,
        role=request.role,
        phone=user_phone,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 7. If user is VENDOR, check if a vendor record already matches email or create placeholder
    vendor_id = None
    if new_user.role == UserRole.VENDOR:
        existing_vendor = db.query(Vendor).filter(Vendor.email == norm_email).first()
        if existing_vendor:
            existing_vendor.user_id = new_user.user_id
            db.commit()
            vendor_id = existing_vendor.vendor_id
        else:
            # Determine vendor details from registration request
            store_name = request.business_name.strip() if request.business_name and request.business_name.strip() else f"{new_user.full_name}'s Store"
            store_cat = request.category.strip() if request.category and request.category.strip() else "General"

            # Validate phone number if provided
            phone_val = "0000000000"
            if request.phone and request.phone.strip():
                is_valid_phone, phone_msg = validate_phone_number(request.phone.strip())
                if not is_valid_phone:
                    raise HTTPException(
                        status_code=422,
                        detail=phone_msg
                    )
                phone_val = phone_msg

            # Auto-create linked vendor profile (starts PENDING until admin activates)
            new_vendor = Vendor(
                business_name=store_name,
                owner_name=new_user.full_name,
                email=norm_email,
                phone=phone_val,
                category=store_cat,
                status=VendorStatus.PENDING,
                user_id=new_user.user_id
            )
            db.add(new_vendor)
            db.commit()
            db.refresh(new_vendor)
            vendor_id = new_vendor.vendor_id

    return UserResponse(
        user_id=new_user.user_id,
        full_name=new_user.full_name,
        email=new_user.email,
        role=new_user.role,
        phone=new_user.phone,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        vendor_id=vendor_id
    )

def authenticate_user(db: Session, request: UserLoginRequest) -> TokenResponse:
    is_valid_email, norm_email = validate_email_format(request.email)
    email_to_check = norm_email if is_valid_email else request.email.strip().lower()

    user = db.query(User).filter(User.email == email_to_check).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deactivated"
        )

    # Enforce role-based portal validation
    if request.role:
        expected_role = request.role.strip().upper()
        user_role_str = user.role.value if hasattr(user.role, "value") else str(user.role).upper()
        if user_role_str != expected_role:
            role_label_map = {
                "ADMIN": "an Admin",
                "VENDOR": "a Vendor",
                "CUSTOMER": "a Customer"
            }
            expected_label = role_label_map.get(expected_role, f"a {expected_role.capitalize()}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This account is not registered as {expected_label}."
            )

    # Find associated vendor id if any
    vendor_id = None
    if user.vendor:
        vendor_id = user.vendor.vendor_id

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role.value,
            "vendor_id": vendor_id
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        vendor_id=vendor_id
    )

def refresh_token(db: Session, current_user: User) -> TokenResponse:
    """Refresh active user JWT access token."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deactivated"
        )

    vendor_id = current_user.vendor.vendor_id if current_user.vendor else None
    new_access_token = create_access_token(
        data={
            "sub": str(current_user.user_id),
            "email": current_user.email,
            "role": current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
            "vendor_id": vendor_id
        }
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        role=current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        vendor_id=vendor_id
    )

def get_user_profile(db: Session, user: User) -> UserResponse:
    vendor_id = user.vendor.vendor_id if user.vendor else None
    return UserResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        phone=user.phone,
        is_active=user.is_active,
        created_at=user.created_at,
        vendor_id=vendor_id
    )
