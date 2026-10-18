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

def test_register_admin_with_passcode_success(client):
    payload = {
        "full_name": "Sreya Admin",
        "email": "sreya_eval_admin@example.com",
        "password": "Password123!",
        "role": "ADMIN",
        "admin_secret": "Admin@123"
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "ADMIN"
    assert data["email"] == "sreya_eval_admin@example.com"
