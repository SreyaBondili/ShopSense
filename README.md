# ShopSense – Multi-Vendor E-Commerce Analytics Platform

**Infosys Springboard Internship Project | Milestone 1 (Weeks 1–2)**

ShopSense is a multi-vendor e-commerce analytics platform designed to help marketplace administrators and individual vendors track sales, manage inventory, and analyze business performance in real time.

This repository contains the complete implementation for **Milestone 1**, which covers vendor onboarding, product catalog management, real-time stock and inventory tracking, transaction processing, and live interactive analytics dashboards.

---

## 📌 Project Overview

In a typical multi-vendor marketplace, managing different sellers, dynamic stock levels, and daily sales numbers across categories can get complicated quickly. ShopSense solves this by separating the concerns into a high-performance **FastAPI REST backend** paired with an interactive **Streamlit dashboard** for visualization.

### What Milestone 1 Delivers:
- **Authentication & RBAC:** Secure JWT-based login with role-based permissions (`ADMIN` and `VENDOR`).
- **Vendor Onboarding:** Seller registration with validation (business name, category, commission rates, duplicate email prevention) and lifecycle statuses (`PENDING`, `ACTIVE`, `SUSPENDED`).
- **Product Catalog:** Full catalog management with search, category filtering, and strict vendor isolation.
- **Inventory Tracking:** Automatic stock synchronization, reorder level alerts, and statuses (`IN STOCK`, `LOW STOCK`, `OUT OF STOCK`).
- **Transaction Processing:** Atomic order placement that validates stock availability and prevents negative inventory.
- **Marketplace Analytics:** Dynamic KPI cards, daily sales trends, product category breakdowns, and top seller rankings using Pandas and Plotly.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Database:** MySQL 8.0, PyMySQL
- **ORM:** SQLAlchemy 2.0
- **Frontend Dashboard:** Streamlit, Plotly
- **Data Analytics:** Pandas
- **Validation & Security:** Pydantic v2, Bcrypt password hashing, PyJWT
- **Testing:** Pytest

---

## 🏗️ System Architecture

```
                 +--------------------------+
                 |  Streamlit Dashboard UI  |
                 |     (Port: 8501)         |
                 +------------+-------------+
                              |
                     REST API | (JWT Bearer)
                              v
                 +--------------------------+
                 |   FastAPI REST Backend   |
                 |     (Port: 8000)         |
                 +------------+-------------+
                              |
                    SQLAlchemy ORM
                              v
                 +--------------------------+
                 |   MySQL 8.0 Database     |
                 |   (Database: shopsense)  |
                 +--------------------------+

Analytics Flow:
MySQL Ledger -> SQLAlchemy -> Pandas DataFrames -> Plotly Visuals -> Streamlit
```

---

## 🗄️ Database Schema

The database consists of 5 normalized relational tables:

1. **`users`** – Stores user credentials, hashed passwords, and assigned roles (`ADMIN` or `VENDOR`).
2. **`vendors`** – Stores vendor business details, contact info, commission rate, and approval status.
3. **`products`** – Stores product catalog items linked to specific vendors.
4. **`inventory`** – Tracks current quantity, warehouse location, and reorder levels per product.
5. **`transactions`** – Immutable log of completed sales orders with item quantities and totals.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- MySQL Server 8.0+ running locally on port `3306`
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/SreyaBondili/ShopSense.git
cd ShopSense
```

### 3. Set Up Virtual Environment & Dependencies
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to create your `.env` file:
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your local MySQL root password:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/shopsense
SECRET_KEY=supersecretjwtkey_shopsense_internship_2026_demo_key_min32chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
API_BASE_URL=http://127.0.0.1:8000
```
*(Note: If your MySQL password has special characters like `@`, URL-encode it, e.g. `%40`)*.

### 5. Initialize Database & Seed Demo Data
```powershell
# Create tables in MySQL
python create_tables.py

# (Optional) Seed realistic demo records
python seed_data.py
```

---

## 💻 Running the Project

You will need **two terminal windows**:

### Terminal 1: Start FastAPI Backend
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Terminal 2: Start Streamlit Dashboard
```powershell
python -m streamlit run dashboard/dashboard.py
```
- Dashboard UI will open at: [http://localhost:8501](http://localhost:8501)

---

## 🔑 Demo Login Credentials

For quick evaluation, use these pre-seeded demo accounts:

| Role | Email | Password | Access Scope |
|---|---|---|---|
| **Admin** | `admin@shopsense.com` | `Admin@123` | Full marketplace access (all vendors, products, inventory, transactions & analytics) |
| **Vendor** | `techworld@example.com` | `Vendor@123` | Apex Electronics (scoped to their own catalog, stock & sales) |
| **Vendor** | `trendsfashion@example.com` | `Vendor@123` | Aura Fashion Hub |
| **Vendor** | `bookoasis@example.com` | `Vendor@123` | Book Haven Store |

*(Or register a new account directly from the login page!)*

---

## 🧪 Running Automated Tests

Run the test suite using pytest:
```powershell
python -m pytest
```

All 25 tests pass successfully, covering:
- Password hashing and JWT generation
- Duplicate email prevention and input validation
- Negative price & stock rejection
- Vendor authorization boundaries (a vendor cannot modify another vendor's goods)
- Atomic transactions & stock deduction consistency
- Live aggregation calculations

---

## 📁 Project Structure

```
ShopSense/
├── app/
│   ├── main.py              # FastAPI app configuration & route mounts
│   ├── config.py            # Environment variables loader
│   ├── database.py          # SQLAlchemy engine & session setup
│   ├── models/              # Database models (User, Vendor, Product, Inventory, Transaction)
│   ├── schemas/             # Pydantic schemas for request & response validation
│   ├── routes/              # API endpoints (/auth, /api/vendors, /api/products, etc.)
│   ├── services/            # Business logic and database queries
│   └── utils/               # Password hashing & validation utilities
├── dashboard/
│   ├── dashboard.py         # Streamlit frontend app
│   └── api_client.py        # HTTP client interacting with FastAPI
├── tests/                   # Pytest test cases
├── create_tables.py         # Table creation script
├── seed_data.py             # Demo data population script
├── requirements.txt         # Project dependencies
├── .env.example             # Sample environment variables
└── README.md                # Documentation
```

---

## 👩‍💻 Author

**Sreya Bondili**  

