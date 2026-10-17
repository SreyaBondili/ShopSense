# ShopSense – Multi-Vendor E-Commerce Analytics Platform
## Milestone 1 Implementation (Weeks 1–2)

ShopSense is an enterprise-grade multi-vendor e-commerce analytics platform engineered with **FastAPI**, **SQLAlchemy ORM**, **MySQL**, **Pandas**, and **Streamlit**. 

Milestone 1 establishes the operational core of the platform: vendor onboarding, catalog management, real-time inventory tracking with automated status categorization, transactional sales execution with atomic stock deduction, and live marketplace analytics powered by Pandas and Plotly.

---

## 1. Project Overview & Milestone 1 Scope

### In-Scope (Milestone 1 Core Deliverables)
- **Vendor Onboarding & Lifecycle Management**: Vendor registration, rigorous field validation (business name, owner, email, phone, category, commission rate), duplicate email prevention, admin approvals, and status tracking (`PENDING`, `ACTIVE`, `SUSPENDED`).
- **Product Catalog Management**: Product creation, categorized cataloging, pricing validation ($> 0$), stock tracking, search, and vendor filtering.
- **Inventory Tracking & Warehouse Management**: Real-time stock counts, warehouse locations, reorder thresholds, dynamic status computation (`IN STOCK`, `LOW STOCK`, `OUT OF STOCK`), and negative stock prevention.
- **Transaction Processing**: Atomic order execution, stock availability checks, automated stock reduction, transaction amount calculation, and purchase logging.
- **Marketplace Analytics Engine**: Live aggregation of total revenue, transaction counts, units sold, average transaction value (ATV), top-performing vendors, top-selling products, category distribution, and time-series sales trends.
- **Enterprise Security**: Bcrypt password hashing, JWT Bearer tokens, and strict role-based access control (`ADMIN` vs `VENDOR`).
- **Interactive UI**: Dual-role Streamlit dashboard integrating directly with the FastAPI REST API backend.

---

## 2. System Architecture

```
User (Browser)
      ↓
Streamlit Frontend (Port 8501)
      ↓ (REST API / JWT Bearer)
FastAPI Backend (Port 8000)
      ↓
SQLAlchemy ORM
      ↓
MySQL Server 8.0 (Database: shopsense)

Analytics Pipeline:
MySQL Transaction Ledger → SQLAlchemy → Pandas DataFrame Aggregation → Plotly Charts → Streamlit UI
```

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend REST API** | FastAPI 0.110+ | Asynchronous RESTful API framework |
| **Server** | Uvicorn | ASGI web server |
| **Database** | MySQL Server 8.0 | Relational primary database |
| **ORM** | SQLAlchemy 2.0+ & PyMySQL | Object-Relational Mapping & MySQL driver |
| **Data Analytics** | Pandas 2.2+ | In-memory aggregations & statistical summaries |
| **Visualizations** | Plotly 5.20+ | Interactive analytics charts (Trends, Pies, Bars) |
| **Data Validation** | Pydantic v2 & Email-Validator | Schema enforcement and field validation |
| **Authentication** | Bcrypt & Python-Jose (JWT) | Password hashing and stateless token auth |
| **Frontend UI** | Streamlit 1.32+ | Interactive multi-page dashboard |
| **Testing** | Pytest 8.0+ | Automated unit, security, and accuracy test suite |
| **Configuration** | Python-Dotenv & Pydantic-Settings | Environment variable management |

---

## 4. Database Schema Design

The `shopsense` database contains 5 core relational tables:

```mermaid
erDiagram
    users ||--o| vendors : "has account"
    vendors ||--o{ products : "manages"
    vendors ||--o{ transactions : "receives"
    products ||--|| inventory : "tracks"
    products ||--o{ transactions : "sold in"

    users {
        int user_id PK
        string full_name
        string email UK
        string password_hash
        string role "ADMIN / VENDOR"
        boolean is_active
        datetime created_at
    }

    vendors {
        int vendor_id PK
        string business_name
        string owner_name
        string email UK
        string phone
        string category
        decimal commission_rate
        string status "ACTIVE / PENDING / SUSPENDED"
        int user_id FK
        datetime created_at
    }

    products {
        int product_id PK
        string product_name
        string category
        decimal price
        int stock
        int vendor_id FK
        datetime created_at
    }

    inventory {
        int inventory_id PK
        int product_id FK
        int current_stock
        string warehouse
        int reorder_level
        datetime updated_at
    }

    transactions {
        int transaction_id PK
        int product_id FK
        int vendor_id FK
        int quantity
        decimal amount
        datetime transaction_date
    }
```

---

## 5. Directory Structure

```
ShopSense/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── database.py              # SQLAlchemy engine and SessionLocal dependency
│   ├── config.py                # Environment settings via Pydantic-Settings
│   │
│   ├── models/                  # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py              # User & UserRole models
│   │   ├── vendor.py            # Vendor & VendorStatus models
│   │   ├── product.py           # Product catalog model
│   │   ├── inventory.py         # Inventory model with status property
│   │   └── transaction.py       # Transaction record model
│   │
│   ├── schemas/                 # Pydantic Request/Response validation schemas
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, register, and token schemas
│   │   ├── vendor.py            # Vendor schemas
│   │   ├── product.py           # Product schemas
│   │   ├── inventory.py         # Inventory schemas
│   │   ├── transaction.py       # Transaction schemas
│   │   └── analytics.py         # Analytics and aggregation schemas
│   │
│   ├── routes/                  # API Endpoint controllers
│   │   ├── __init__.py
│   │   ├── auth.py              # /auth/register, /auth/login, /auth/me
│   │   ├── vendors.py           # /api/vendors CRUD
│   │   ├── products.py          # /api/products CRUD
│   │   ├── inventory.py         # /api/inventory tracking & updates
│   │   ├── transactions.py      # /api/transactions execution
│   │   └── analytics.py         # /api/analytics aggregations
│   │
│   ├── services/                # Business logic & Database transactions
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Registration & authentication logic
│   │   ├── vendor_service.py    # Vendor lifecycle & validation logic
│   │   ├── product_service.py   # Product & auto-inventory logic
│   │   ├── inventory_service.py # Stock management & threshold checks
│   │   ├── transaction_service.py # Atomic sales & stock reduction
│   │   └── analytics_service.py # Pandas marketplace aggregation engine
│   │
│   └── utils/
│       ├── __init__.py
│       ├── security.py          # Bcrypt hashing & JWT Bearer token logic
│       └── validators.py        # Strict regex & RFC field validators
│
├── dashboard/
│   ├── dashboard.py             # Streamlit interactive UI application
│   └── api_client.py            # Python REST client communicating with FastAPI
│
├── tests/                       # Pytest automated test suite (25 tests)
│   ├── conftest.py              # In-memory test database & auth fixtures
│   ├── test_auth.py             # Tests for auth, JWT, hashing, duplicate prevention
│   ├── test_vendors.py          # Tests for onboarding, 100% validation, RBAC
│   ├── test_products.py         # Tests for catalog, pricing, vendor isolation
│   ├── test_inventory.py        # Tests for stock levels, negative stock prevention
│   ├── test_transactions.py     # Tests for order execution, 100% consistency
│   └── test_analytics.py        # Tests for KPI summaries, vendor & product metrics
│
├── test_db.py                   # Pre-flight MySQL connection diagnostic tool
├── create_tables.py             # Schema migration script (creates MySQL tables)
├── seed_data.py                 # Realistic demo data populator (5 vendors, 15 products, 37 txs)
├── requirements.txt             # Project dependencies
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Template for environment variables
├── .gitignore                   # Git ignore patterns
└── README.md                    # Comprehensive documentation
```

---

## 6. Installation & Setup Guide

### Step 1: Clone or Navigate to the Workspace
```powershell
cd C:\Users\Dell\.gemini\antigravity\scratch\ShopSense
```
*(A synchronized copy is also available at `D:\ShopSense`)*

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your MySQL password:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/shopsense
SECRET_KEY=supersecretjwtkey_shopsense_internship_2026_demo_key_min32chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
API_BASE_URL=http://127.0.0.1:8000
```

### Step 3: Verify MySQL Connection
Run the diagnostic script to verify your credentials and ensure the `shopsense` database is ready:
```powershell
.\.venv\Scripts\python.exe test_db.py
```

### Step 4: Create Database Tables
Execute the table creation script:
```powershell
.\.venv\Scripts\python.exe create_tables.py
```

### Step 5: Seed Realistic Demo Data
Populate the database with 5 vendors, 15 categorized products, inventory records, and 37 historical transactions:
```powershell
.\.venv\Scripts\python.exe seed_data.py
```

---

## 7. Running the Application

### 1. Launch FastAPI Backend
In Terminal 1:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Interactive ReDoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Launch Streamlit UI
In Terminal 2:
```powershell
.\.venv\Scripts\streamlit.exe run dashboard/dashboard.py
```
Streamlit will automatically open at: [http://localhost:8501](http://localhost:8501)

---

## 8. Demo User Credentials

The database comes pre-seeded with accounts ready for evaluation:

| Role | Name | Email | Password | Access Scope |
|---|---|---|---|---|
| **ADMIN** | Marketplace Administrator | `admin@shopsense.com` | `Admin@123` | Full access to all vendors, products, inventory, transactions, and marketplace analytics |
| **VENDOR** | John Doe (Apex Electronics) | `techworld@example.com` | `Vendor@123` | Scoped to Apex Electronics catalog, transactions, and performance metrics |
| **VENDOR** | Sarah Miller (Aura Fashion Hub) | `trendsfashion@example.com` | `Vendor@123` | Scoped to Aura Fashion Hub catalog, transactions, and performance metrics |
| **VENDOR** | Robert Clark (Book Haven Store) | `bookoasis@example.com` | `Vendor@123` | Scoped to Book Haven Store catalog, transactions, and performance metrics |
| **VENDOR** | Emma Watson (Urban Home) | `homecomforts@example.com` | `Vendor@123` | Scoped to Urban Home catalog, transactions, and performance metrics |
| **VENDOR** | Priya Sharma (Glow Cosmetics) | `glowbeauty@example.com` | `Vendor@123` | Scoped to Glow Cosmetics catalog, transactions, and performance metrics |

*Note: The login page includes 1-click **Quick Demo Login** buttons for instant testing.*

---

## 9. API Reference

### Authentication (`/auth`)
- `POST /auth/register`: Register a new user (`ADMIN` or `VENDOR`).
- `POST /auth/login`: Authenticate and receive a JWT Bearer token.
- `GET /auth/me`: Get profile and role details of the authenticated user.

### Vendor Management (`/api/vendors`)
- `POST /api/vendors`: Onboard a new vendor (with 100% field validation).
- `GET /api/vendors`: List vendors (Admins view all; Vendors view own).
- `GET /api/vendors/{vendor_id}`: Retrieve single vendor details.
- `PUT /api/vendors/{vendor_id}`: Update vendor information (Status modifications restricted to Admin).
- `DELETE /api/vendors/{vendor_id}`: Admin-only deletion of vendor.

### Product Catalog (`/api/products`)
- `POST /api/products`: Add product and automatically initialize inventory.
- `GET /api/products`: Query catalog with category, vendor, and keyword search filters.
- `GET /api/products/{product_id}`: Retrieve single product details.
- `PUT /api/products/{product_id}`: Update product price or stock (synchronizes with inventory).
- `DELETE /api/products/{product_id}`: Remove product from catalog.

### Inventory Management (`/api/inventory`)
- `GET /api/inventory`: Retrieve inventory levels with calculated status (`IN STOCK`, `LOW STOCK`, `OUT OF STOCK`).
- `GET /api/inventory/{product_id}`: Retrieve stock tracking for specific product.
- `PUT /api/inventory/{product_id}`: Restock, adjust reorder thresholds, or change warehouse location.

### Transactions (`/api/transactions`)
- `POST /api/transactions`: Process an order with atomic stock verification and automated decrement.
- `GET /api/transactions`: Retrieve transaction ledger (scoped to role).
- `GET /api/transactions/{transaction_id}`: Retrieve single transaction record.

### Analytics & Reporting (`/api/analytics`)
- `GET /api/analytics/summary`: High-level KPIs (Total Revenue, Transactions, Units Sold, ATV).
- `GET /api/analytics/vendor-performance`: Vendor rankings by revenue and volume.
- `GET /api/analytics/product-performance`: Product ranking, stock status, and units sold.
- `GET /api/analytics/revenue-trend`: Time-series daily revenue breakdown.
- `GET /api/analytics/category-performance`: Revenue and volume grouped by product category.

---

## 10. Automated Testing & Verification

Run the complete test suite:
```powershell
.\.venv\Scripts\python.exe -m pytest
```

### Verified Test Results
```text
tests/test_analytics.py::test_analytics_metrics_and_role_scoping PASSED
tests/test_auth.py::test_password_hashing PASSED
tests/test_auth.py::test_register_user_success PASSED
tests/test_auth.py::test_register_duplicate_email_conflict PASSED
tests/test_auth.py::test_register_invalid_email PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_get_current_user_profile PASSED
tests/test_auth.py::test_get_current_user_unauthorized PASSED
tests/test_inventory.py::test_inventory_lifecycle_and_status PASSED
tests/test_inventory.py::test_inventory_negative_stock_rejection PASSED
tests/test_products.py::test_create_product_by_vendor PASSED
tests/test_products.py::test_product_validation_negative_price PASSED
tests/test_products.py::test_product_validation_negative_stock PASSED
tests/test_products.py::test_vendor_cannot_modify_other_vendor_product PASSED
tests/test_transactions.py::test_transaction_creation_and_stock_reduction PASSED
tests/test_transactions.py::test_transaction_insufficient_stock_rejection PASSED
tests/test_transactions.py::test_transaction_invalid_quantity PASSED
tests/test_transactions.py::test_transaction_and_revenue_consistency_exceeds_98_percent PASSED (Consistency: 100.00%)
tests/test_vendors.py::test_vendor_validation_accuracy_exceeds_99_percent PASSED (Accuracy: 100.00%)
tests/test_vendors.py::test_create_vendor_by_admin PASSED
tests/test_vendors.py::test_create_vendor_duplicate_email PASSED
tests/test_vendors.py::test_vendor_rbac_cannot_view_other_vendor PASSED
tests/test_vendors.py::test_admin_can_update_vendor_status PASSED
tests/test_vendors.py::test_vendor_cannot_change_own_status PASSED

======================= 25 passed in 12.21s =======================
```

---

## 11. Milestone 1 Acceptance Criteria Checklist

- [x] **MySQL Database integration**: Clean SQLAlchemy ORM models with foreign key constraints.
- [x] **Authentication**: Bcrypt password hashing + stateless JWT access tokens.
- [x] **Role-Based Access Control**: Backend-enforced authorization for `ADMIN` and `VENDOR`.
- [x] **Vendor Onboarding**: Complete lifecycle handling (`PENDING`, `ACTIVE`, `SUSPENDED`).
- [x] **Vendor Validation**: Rigorous field validators demonstrating **100% accuracy** ($\ge 99\%$).
- [x] **Product Catalog**: Full CRUD with search, category filtering, and vendor isolation.
- [x] **Inventory Management**: Reorder levels, negative stock prevention, and dynamic status computation.
- [x] **Transaction Processing**: Atomic order execution with automated stock reduction.
- [x] **Data Consistency**: Verified **100% transaction and revenue consistency** ($\ge 98\%$).
- [x] **Live Sales Aggregation**: Dynamic metrics calculated by Pandas directly from MySQL transaction records.
- [x] **Streamlit UI**: Full dual-role interactive portal with Plotly visualizations and CSV exports.
- [x] **API Documentation**: Automated OpenAPI/Swagger documentation at `/docs` and ReDoc at `/redoc`.
- [x] **25/25 Pytest Tests Passing**.
