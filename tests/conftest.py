import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.transaction import Transaction
from app.utils.security import hash_password, create_access_token

# In-memory SQLite database dedicated for fast, isolated test execution
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

@pytest.fixture
def db():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db):
    user = User(
        full_name="System Admin",
        email="test_admin@shopsense.com",
        password_hash=hash_password("AdminSecurePass123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": str(admin_user.user_id), "email": admin_user.email, "role": admin_user.role.value})

@pytest.fixture
def vendor_user(db):
    user = User(
        full_name="Jane Vendor",
        email="jane_vendor@example.com",
        password_hash=hash_password("VendorSecurePass123!"),
        role=UserRole.VENDOR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    vendor = Vendor(
        business_name="Jane's Tech Boutique",
        owner_name="Jane Vendor",
        email="jane_vendor@example.com",
        phone="9876543210",
        category="Electronics",
        commission_rate=10.0,
        status=VendorStatus.ACTIVE,
        user_id=user.user_id
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return user

@pytest.fixture
def vendor_token(vendor_user):
    return create_access_token(data={"sub": str(vendor_user.user_id), "email": vendor_user.email, "role": vendor_user.role.value, "vendor_id": vendor_user.vendor.vendor_id})

@pytest.fixture
def other_vendor_user(db):
    user = User(
        full_name="Bob Vendor",
        email="bob_vendor@example.com",
        password_hash=hash_password("BobSecurePass123!"),
        role=UserRole.VENDOR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    vendor = Vendor(
        business_name="Bob's Fashion Den",
        owner_name="Bob Vendor",
        email="bob_vendor@example.com",
        phone="9123456780",
        category="Fashion",
        commission_rate=12.0,
        status=VendorStatus.ACTIVE,
        user_id=user.user_id
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return user

@pytest.fixture
def other_vendor_token(other_vendor_user):
    return create_access_token(data={"sub": str(other_vendor_user.user_id), "email": other_vendor_user.email, "role": other_vendor_user.role.value, "vendor_id": other_vendor_user.vendor.vendor_id})
