import re
from typing import Tuple, List, Optional
from email_validator import validate_email as ext_validate_email, EmailNotValidError

PHONE_REGEX = re.compile(r"^(\+?[1-9]\d{0,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\-.\s]{7,15}$")
NAME_REGEX = re.compile(r"^[a-zA-Z\s\.\-']{2,120}$")
BUSINESS_NAME_REGEX = re.compile(r"^[a-zA-Z0-9\s\.\&\'\-\,\(\)]{2,150}$")

VALID_CATEGORIES = {
    "Electronics", "Fashion", "Books", "Home & Kitchen", "Beauty & Personal Care",
    "Sports & Fitness", "Automotive", "Toys & Games", "Health & Wellness", "Grocery"
}

def validate_email_format(email: str) -> Tuple[bool, str]:
    """Validate email format using RFC standards."""
    if not email or not isinstance(email, str):
        return False, "Email address is required"
    email = email.strip()
    try:
        validated = ext_validate_email(email, check_deliverability=False)
        return True, validated.normalized
    except EmailNotValidError as e:
        return False, f"Invalid email format: {str(e)}"
    except Exception:
        # Fallback regex if library encounters edge issues
        simple_pattern = r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]{2,}$"
        if re.match(simple_pattern, email):
            return True, email.lower()
        return False, "Invalid email format"

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """Validate phone numbers supporting national and international formats."""
    if not phone or not isinstance(phone, str):
        return False, "Phone number is required"
    phone_clean = phone.strip()
    digits_only = re.sub(r"\D", "", phone_clean)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False, f"Phone number must contain between 10 and 15 digits (got {len(digits_only)})"
    if not PHONE_REGEX.match(phone_clean):
        return False, "Phone number contains invalid formatting characters"
    return True, phone_clean

def validate_business_name(name: str) -> Tuple[bool, str]:
    """Validate business/store name."""
    if not name or not isinstance(name, str):
        return False, "Business name is required"
    clean = name.strip()
    if len(clean) < 2 or len(clean) > 150:
        return False, "Business name must be between 2 and 150 characters"
    if not BUSINESS_NAME_REGEX.match(clean):
        return False, "Business name contains invalid characters"
    return True, clean

def validate_owner_name(name: str) -> Tuple[bool, str]:
    """Validate owner/contact person name."""
    if not name or not isinstance(name, str):
        return False, "Owner name is required"
    clean = name.strip()
    if len(clean) < 2 or len(clean) > 120:
        return False, "Owner name must be between 2 and 120 characters"
    if not NAME_REGEX.match(clean):
        return False, "Owner name should only contain letters, spaces, hyphens, and periods"
    return True, clean

def validate_category(category: str) -> Tuple[bool, str]:
    """Validate product/vendor category."""
    if not category or not isinstance(category, str):
        return False, "Category is required"
    clean = category.strip()
    if len(clean) < 2 or len(clean) > 80:
        return False, "Category must be between 2 and 80 characters"
    return True, clean

def validate_vendor_registration(data: dict) -> List[str]:
    """Validate all fields for vendor registration and return list of validation errors."""
    errors = []
    
    # Business name
    b_ok, b_msg = validate_business_name(data.get("business_name", ""))
    if not b_ok:
        errors.append(b_msg)

    # Owner name
    o_ok, o_msg = validate_owner_name(data.get("owner_name", ""))
    if not o_ok:
        errors.append(o_msg)

    # Email
    e_ok, e_msg = validate_email_format(data.get("email", ""))
    if not e_ok:
        errors.append(e_msg)

    # Phone
    p_ok, p_msg = validate_phone_number(data.get("phone", ""))
    if not p_ok:
        errors.append(p_msg)

    # Category
    c_ok, c_msg = validate_category(data.get("category", ""))
    if not c_ok:
        errors.append(c_msg)

    # Commission rate (optional, default 10%)
    if "commission_rate" in data and data["commission_rate"] is not None:
        try:
            comm = float(data["commission_rate"])
            if comm < 0.0 or comm > 100.0:
                errors.append("Commission rate must be between 0.0% and 100.0%")
        except (ValueError, TypeError):
            errors.append("Commission rate must be a valid number")

    return errors
