# ShopSense — Authentication & Session Management Fix Report

**Date:** November 17, 2026  
**System:** ShopSense Multi-Vendor E-Commerce Analytics Platform  
**Target Environment:** FastAPI (Python 3.13), React 18 + Vite, MySQL 8.0, SQLAlchemy, JWT (python-jose)  
**Status:** **ALL ISSUES RESOLVED & VERIFIED (PASS)**

---

## Executive Summary

Two critical authentication and session stability issues in the ShopSense application have been investigated, resolved, and verified:
1. **Issue 1 (Login Loading Problem):** The login button stayed indefinitely on *"Authenticating..."* without navigating to role-specific dashboards.
2. **Issue 2 (Automatic Logout After Inactivity):** Users were prematurely redirected to the login page during normal inactivity without clear feedback.

Both issues have been resolved at the architectural and code levels across the frontend, API transport layer, FastAPI backend, and background scheduler services. No UI redesign was required, all existing features and database records remain intact, and all security boundaries (RBAC, JWT signature verification) have been maintained.

---

## 1. Root Cause Analysis

### Issue 1: Login Loading Problem ("Authenticating..." Spinner Freeze)

1. **Corrupted Model File on Backend:**
   - In `app/models/inventory.py` (Line 1), an accidental PowerShell command prefix (`Start-Process "http://localhost:3000"from sqlalchemy import...`) introduced a fatal `SyntaxError`. This prevented the uvicorn worker from completing module reloading upon server restart, leaving the API unreachable.
2. **Zombie Backend Process & Connection Lock:**
   - A background uvicorn process (PID 22312) was occupying port 8000 in a hung state. New incoming HTTP connections from the frontend Vite proxy (`/auth/login`) timed out after 60 seconds or hung indefinitely.
3. **Missing Request Timeout in Frontend Client:**
   - In `frontend/src/api.js`, the `fetch()` wrapper lacked an `AbortController` or timeout mechanism. When network calls stalled or backend was unresponsive, the Promise remained pending indefinitely, keeping `loading = true` on the button.
4. **Base64URL Encoding Decoding Failure:**
   - In `frontend/src/api.js` (`isTokenExpired`), the JWT token payload was decoded using `atob(parts[1])`. RFC 7515 Base64URL-encoded tokens containing `-` or `_` or omitting `=` padding caused `atob()` to throw an `InvalidCharacterError`, leaving the authentication cycle unhandled.
5. **Missing Pre-Submit Validation in Login Component:**
   - In `frontend/src/pages/LoginPage.jsx`, if a user submitted the form without credentials, the state was immediately switched to `loading: true` without client-side guards, relying exclusively on backend validation without local recovery fallback.

---

### Issue 2: Automatic Logout After Inactivity

1. **Destructive Mount Effect in `LoginPage.jsx`:**
   - `LoginPage.jsx` contained an aggressive `useEffect` hook:
     ```javascript
     useEffect(() => {
       localStorage.removeItem('shopsense_token');
       localStorage.removeItem('shopsense_user');
       sessionStorage.clear();
     }, []);
     ```
     Any time `LoginPage` mounted—even during momentary state transitions or URL hash changes—it immediately purged valid authentication credentials from storage.
2. **Asynchronous Initial State Race Condition in `App.jsx`:**
   - `App.jsx` initialized the current user state as `useState(null)`. On application reload or navigation, React rendered before the asynchronous `useEffect` retrieved the user from storage. Because `user` was temporarily `null`, the app rendered `<LoginPage />`, immediately triggering the destructive mount effect that wiped valid session tokens.
3. **Hard Page Reloads Erasing User Notifications:**
   - Logout events called `window.location.replace('/')`, forcing a hard browser refresh that instantly erased all in-memory React toast notifications and error messages before the user could read why they were logged out.
4. **Absence of a Token Refresh Flow:**
   - The backend lacked a dedicated refresh endpoint (`POST /auth/refresh`). When tokens approached expiration, the client could not refresh credentials in the background during active sessions.
5. **Database Connection Leak in Background Scheduler:**
   - APScheduler jobs in `app/scheduler/scheduler_service.py` (`_execute_retrain_job` and `_execute_analytics_refresh_job`) invoked `next(get_db())` without a corresponding `close()` in a `finally` block. Over time, leaked connections exhausted the MySQL pool, resulting in sporadic `500 Internal Server Error` responses on JWT user lookups (`get_current_active_user`).

---

## 2. Technical Fixes Implemented

### Backend Improvements

| File | Changes Made |
| :--- | :--- |
| `app/models/inventory.py` | Removed the corrupted PowerShell prefix on line 1, restoring valid SQLAlchemy imports. |
| `app/services/auth_service.py` | Implemented `refresh_token(db, current_user)`: verifies user status in database, revokes previous session if needed, issues a refreshed JWT with renewed expiration. |
| `app/routes/auth.py` | Added `@router.post("/auth/refresh", response_model=TokenResponse)` protected endpoint. |
| `app/scheduler/scheduler_service.py` | Replaced unclosed `next(get_db())` calls with `SessionLocal()` wrapped in strict `try ... finally: db.close()` blocks. |
| `app/main.py` | Enhanced CORS configuration with explicit localhost origins and regex support. |

### Frontend Improvements

| File | Changes Made |
| :--- | :--- |
| `frontend/src/api.js` | 1. Implemented 15-second `AbortController` timeout for all API requests.<br>2. Fixed Base64URL parsing in `isTokenExpired()` with character replacement (`-` &rarr; `+`, `_` &rarr; `/`) and `=` padding.<br>3. Added `api.refreshToken()` method.<br>4. Enhanced 401 handling to trigger graceful SPA logout with session expiration notice. |
| `frontend/src/App.jsx` | 1. Initialized state synchronously: `useState(() => api.getUser())`.<br>2. Implemented 60-minute user inactivity manager tracking user interaction events (`mousedown`, `keydown`, `scroll`, `touchstart`, `click`).<br>3. Added proactive token refresh every 15 minutes during active sessions.<br>4. Replaced destructive `window.location.replace('/')` with hash-based SPA logout (`window.location.hash = '#/'`) and session-expired alert messaging. |
| `frontend/src/pages/LoginPage.jsx` | 1. Removed destructive credentials-wiping `useEffect`.<br>2. Added `sessionStorage.getItem('shopsense_session_expired_msg')` banner display.<br>3. Added client-side empty credential guards with immediate feedback.<br>4. Enforced automatic redirection on successful login to correct role portals (`/admin`, `/vendor`, `/customer`). |
| `frontend/vite.config.js` | Added `changeOrigin: true` to `/auth` and `/api` proxy configurations to ensure seamless reverse proxy header rewriting. |

---

## 3. Test & Verification Results

### Automated Regression Suite

- **Authentication Suite (`tests/test_auth.py`):** **25/25 PASSED**
  - Includes new tests: `test_refresh_token_success`, `test_refresh_token_unauthorized`.
  - Admin, Vendor, and Customer registration and login: **PASSED**.
  - Password hashing and tampering rejection: **PASSED**.
- **Milestone 2 Services (`tests/test_milestone2.py`):** **8/8 PASSED**
- **Milestone 3 Services (`tests/test_milestone3_services.py`):** **7/7 PASSED**
- **Workflow Automation (`tests/test_workflow_automation.py`):** **4/4 PASSED**
- **Dashboard Consistency (`tests/test_dashboard_consistency.py`):** **3/3 PASSED** (Admin 10/10, Vendor 43/43, Customer 20/20 &mdash; 100% KPI match).

### Live Endpoints Verification

1. **Role-Based Authentication:**
   - **Admin Login (`bsreya1610@gmail.com`):** `200 OK` &rarr; Returns JWT token & role `"admin"`.
   - **Vendor Login (`techworld@example.com`):** `200 OK` &rarr; Returns JWT token & role `"vendor"`.
   - **Customer Login (`customer@shopsense.com`):** `200 OK` &rarr; Returns JWT token & role `"customer"`.
2. **Error & RBAC Security:**
   - **Invalid Password:** `401 Unauthorized` with `"Invalid email or password"`.
   - **Role Portal Mismatch:** `403 Forbidden` with `"This account is not registered as an Admin."`.
   - **Token Refresh:** `200 OK` with updated `access_token` and `token_type: "bearer"`.

### Database Integrity Check

All MySQL tables in `shopsense` were verified before and after modifications:
- `users`: 128 records (All Admin, Vendor, Customer profiles intact)
- `transactions`: 1,198 historical transaction records intact
- `products` & `inventory`: 100% preserved
- Total Revenue Metric: ₹407,741.80 (100% consistent with audit baseline)

---

## 4. Conclusion

Both critical authentication issues are completely resolved. The application now features:
- Rapid and resilient authentication with timeout protection.
- Correct role-based dashboard redirects for Admin, Vendor, and Customer users.
- Robust 60-minute inactivity session tracking without unprompted logouts during regular usage.
- Transparent session expiration messages informing users when re-authentication is needed.
- Leak-free backend database connection pooling and zero regressions across all Milestone 1, 2, and 3 capabilities.
