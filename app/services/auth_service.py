from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.validators import validate_email_format, validate_owner_name, validate_phone_number

def register_user(db: Session, request: UserRegisterRequest) -> UserResponse:
    # 0. Block public admin registration unless authorized with Admin Security Passcode
    if request.role == UserRole.ADMIN:
        if not request.admin_secret or request.admin_secret.strip() != "Admin@123":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin accounts cannot be created through public registration without a valid Admin Security Passcode."
            )

    # 1. Validate email format
    is_valid_email, norm_email = validate_email_format(request.email)
    if not is_valid_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=name_msg
        )

    # 4. Hash password
    hashed_pw = hash_password(request.password)

    # 5. Create user
    new_user = User(
        full_name=request.full_name.strip(),
        email=norm_email,
        password_hash=hashed_pw,
        role=request.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 6. If user is VENDOR, check if a vendor record already matches email or create placeholder
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
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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

def get_user_profile(db: Session, user: User) -> UserResponse:
    vendor_id = user.vendor.vendor_id if user.vendor else None
    return UserResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        vendor_id=vendor_id
    )
