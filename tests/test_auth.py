import pytest
from app.utils.security import hash_password, verify_password

def test_password_hashing():
    raw_pass = "MySecretPass#2026"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_register_user_success(client):
    payload = {
        "full_name": "Alice Wonder",
        "email": "alice@example.com",
        "password": "Password123!",
        "role": "VENDOR"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "VENDOR"
    assert "user_id" in data
    assert "password_hash" not in data

def test_register_duplicate_email_conflict(client):
    payload = {
        "full_name": "Duplicate User",
        "email": "dup@example.com",
        "password": "Password123!",
        "role": "VENDOR"
    }
    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 409
    assert "already registered" in resp2.json()["detail"].lower()

def test_register_invalid_email(client):
    payload = {
        "full_name": "Bad Email User",
        "email": "not-an-email",
        "password": "Password123!",
        "role": "VENDOR"
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 422

def test_login_success(client, admin_user):
    payload = {
        "email": admin_user.email,
        "password": "AdminSecurePass123!"
    }
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "ADMIN"
    assert data["email"] == admin_user.email

def test_login_invalid_password(client, admin_user):
    payload = {
        "email": admin_user.email,
        "password": "IncorrectPassword"
    }
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == 401
    assert "invalid email or password" in resp.json()["detail"].lower()

# ----------------- Role-Based Portal Login Matrix Tests -----------------
def test_login_with_role_admin_success(client, admin_user):
    resp = client.post("/auth/login", json={
        "email": admin_user.email,
        "password": "AdminSecurePass123!",
        "role": "ADMIN"
    })
    assert resp.status_code == 200
    assert resp.json()["role"] == "ADMIN"

def test_login_admin_credentials_in_vendor_portal_rejected(client, admin_user):
    resp = client.post("/auth/login", json={
        "email": admin_user.email,
        "password": "AdminSecurePass123!",
        "role": "VENDOR"
    })
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This account is not registered as a Vendor."

def test_login_admin_credentials_in_customer_portal_rejected(client, admin_user):
    resp = client.post("/auth/login", json={
        "email": admin_user.email,
        "password": "AdminSecurePass123!",
        "role": "CUSTOMER"
    })
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This account is not registered as a Customer."

def test_login_with_role_vendor_success(client, vendor_user):
    resp = client.post("/auth/login", json={
        "email": vendor_user.email,
        "password": "VendorSecurePass123!",
        "role": "VENDOR"
    })
    assert resp.status_code == 200
    assert resp.json()["role"] == "VENDOR"

def test_login_vendor_credentials_in_admin_portal_rejected(client, vendor_user):
    resp = client.post("/auth/login", json={
        "email": vendor_user.email,
        "password": "VendorSecurePass123!",
        "role": "ADMIN"
    })
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This account is not registered as an Admin."

def test_login_vendor_credentials_in_customer_portal_rejected(client, vendor_user):
    resp = client.post("/auth/login", json={
        "email": vendor_user.email,
        "password": "VendorSecurePass123!",
        "role": "CUSTOMER"
    })
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This account is not registered as a Customer."

def test_login_with_role_customer_success(client, customer_user):
    resp = client.post("/auth/login", json={
        "email": customer_user.email,
        "password": "CustomerSecurePass123!",
        "role": "CUSTOMER"
    })
    assert resp.status_code == 200
    assert resp.json()["role"] == "CUSTOMER"

def test_login_customer_credentials_in_admin_portal_rejected(client, customer_user):
    resp = client.post("/auth/login", json={
        "email": customer_user.email,
        "password": "CustomerSecurePass123!",
        "role": "ADMIN"
    })
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This account is not registered as an Admin."

def test_login_customer_credentials_in_vendor_portal_rejected(client, customer_user):
    resp = client.post("/auth/login", json={
        "email": customer_user.email,
        "password": "CustomerSecurePass123!",
        "role": "VENDOR"
    })
    assert resp.status_code == 403
    assert resp.json()["detail"] == "This account is not registered as a Vendor."

def test_get_current_user_profile(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test_admin@shopsense.com"
    assert data["role"] == "ADMIN"

def test_get_current_user_unauthorized(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid_or_expired_token"})
    assert resp.status_code == 401

def test_register_admin_blocked(client):
    payload = {
        "full_name": "Wannabe Admin",
        "email": "hacker_admin@example.com",
        "password": "Password123!",
        "role": "ADMIN"
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 403
    assert "admin accounts cannot be created through public registration" in resp.json()["detail"].lower()

def test_register_password_over_72_bytes(client):
    long_pw = "A" * 73
    payload = {
        "full_name": "Long Password User",
        "email": "longpw@example.com",
        "password": long_pw,
        "role": "VENDOR"
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 422
    assert "72 bytes" in str(resp.json()).lower()

def test_register_admin_with_old_default_secret_rejected(client):
    payload = {
        "full_name": "Attacker Admin",
        "email": "attacker_admin@example.com",
        "password": "Password123!",
        "role": "ADMIN",
        "admin_secret": "Admin@123"  # Old exposed default must be rejected
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 403
    assert "admin accounts cannot be created" in resp.json()["detail"].lower()

def test_register_admin_with_passcode_success(client):
    from app.config import settings
    payload = {
        "full_name": "Sreya Admin",
        "email": "sreya_eval_admin@example.com",
        "password": "Password123!",
        "role": "ADMIN",
        "admin_secret": settings.ADMIN_REGISTRATION_SECRET
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "ADMIN"
    assert data["email"] == "sreya_eval_admin@example.com"

def test_customer_registration_mandatory_phone_validation(client):
    # Missing phone number -> 422
    no_phone_payload = {
        "full_name": "Customer No Phone",
        "email": "cust_nophone@example.com",
        "password": "Password123!",
        "role": "CUSTOMER"
    }
    r1 = client.post("/auth/register", json=no_phone_payload)
    assert r1.status_code == 422
    assert "phone" in str(r1.json()).lower()

    # Invalid phone number -> 422
    bad_phone_payload = {
        "full_name": "Customer Bad Phone",
        "email": "cust_badphone@example.com",
        "password": "Password123!",
        "role": "CUSTOMER",
        "phone": "12345"
    }
    r2 = client.post("/auth/register", json=bad_phone_payload)
    assert r2.status_code == 422
    assert "digit" in str(r2.json()).lower()

    # Valid Indian phone number with +91 -> 201
    good_phone_payload = {
        "full_name": "Customer Indian Phone",
        "email": "cust_indianphone@example.com",
        "password": "Password123!",
        "role": "CUSTOMER",
        "phone": "+91 9876543210"
    }
    r3 = client.post("/auth/register", json=good_phone_payload)
    assert r3.status_code == 201
    data = r3.json()
    assert data["role"] == "CUSTOMER"
    assert data["phone"] == "+91 9876543210"

def test_vendor_registration_general_category(client):
    payload = {
        "full_name": "General Store Owner",
        "email": "general_vendor@example.com",
        "password": "Password123!",
        "role": "VENDOR",
        "phone": "9876543211",
        "business_name": "Metro General Megastore",
        "category": "General"
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "VENDOR"

def test_refresh_token_success(client, customer_token):
    # Refresh token using valid Bearer token
    ref_resp = client.post("/auth/refresh", headers={"Authorization": f"Bearer {customer_token}"})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    assert "access_token" in ref_data
    assert ref_data["role"] == "CUSTOMER"
    assert ref_data["email"] == "customer_test@example.com"

def test_refresh_token_unauthorized(client):
    ref_resp = client.post("/auth/refresh")
    assert ref_resp.status_code == 401
