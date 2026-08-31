# Employee Leave & Attendance Management System

A full-stack, role-based **Employee Leave & Attendance Management System** built with **Django REST Framework** (backend) and **React** (frontend), with **JWT authentication**, **PostgreSQL/SQLite**, and full test coverage.

This project demonstrates: backend architecture, relational database design, authentication & authorization (JWT + role-based access), REST APIs, validation, query optimization, file/media handling, testing, Git workflow, and production deployment concepts (Docker, Gunicorn, Nginx, environment variables).

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Roles & Permissions](#roles--permissions)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Database Design](#database-design)
6. [Live Credentials (Demo Users)](#live-credentials-demo-users)
7. [Installation & Setup](#installation--setup)
   - [Option A: Quick Setup (with SQLite)](#option-a-quick-setup-with-sqlite)
   - [Option B: Setup with PostgreSQL](#option-b-setup-with-postgresql)
   - [Frontend Setup](#frontend-setup)
8. [Run the Tests](#run-the-tests)
9. [API Documentation](#api-documentation)
10. [Authentication Flow](#authentication-flow)
11. [Docker Deployment](#docker-deployment)
12. [Deployment to Production](#deployment-to-production)
13. [Key Implementation Details](#key-implementation-details)

---

## Project Overview

Organizations can manage **employee information, attendance records, and leave requests**. The system supports three roles — **Employee**, **Manager**, and **Administrator** — each with restricted access to only the data and operations their role permits.

### Features

- **Employee**
  - Check-in / check-out for daily attendance
  - View own attendance history and monthly summary
  - Apply for leave (with automatic leave-balance validation)
  - View own leave requests and leave balances
  - Cancel a pending request
  - Update own profile & change password

- **Manager**
  - Everything an employee can do
  - View attendance of their department / team
  - Approve or reject leave requests from their team

- **Administrator**
  - Full access to everything
  - Create/manage departments
  - Create users and assign roles (admin / manager / employee)
  - Activate / deactivate users
  - Manage all leave types and balances

---

## Roles & Permissions

| Role | Register | Manage own attendance | View team attendance | Create leave | Approve leave | Manage users | Manage departments |
|------|:--------:|:---------------------:|:--------------------:|:------------:|:-------------:|:------------:|:------------------:|
| Employee | Yes | Yes | No | Yes | No | No | No |
| Manager | Yes | Yes | Yes (own team) | Yes | Yes | No | No |
| Admin | Yes | Yes | Yes (all) | Yes | Yes | Yes | Yes |

Access is enforced both in **views** (DRF permissions) and in the **querysets** (row-level scoping), so employees can never see another user's data.

---

## Tech Stack

**Backend**
- Python 3.12
- Django 6.x
- Django REST Framework
- SimpleJWT (JWT authentication)
- django-filter (filtering/search/ordering)
- django-cors-headers
- python-decouple (environment configuration)
- Pillow (image upload for avatars)
- whitenoise (static files in production)
- gunicorn (WSGI server)
- psycopg2-binary (PostgreSQL driver)

**Frontend**
- React 18
- Vite 5
- React Router DOM 6
- Axios (with JWT refresh interceptor)

**Database**
- PostgreSQL (production/recommended) or SQLite (development default)

**Deployment**
- Docker / docker-compose
- Gunicorn
- Nginx

---

## Project Structure

```
leave_management/
├── backend/                        # Django project
│   ├── core/                       # Project settings, urls, middleware, exceptions, permissions, pagination
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── middleware.py           # Request logging middleware
│   │   ├── exceptions.py           # Custom DRF exception handler
│   │   ├── permissions.py          # Shared role permissions
│   │   ├── pagination.py           # Standard pagination
│   │   └── tests_api.py            # Unit + API + permission + validation tests
│   ├── accounts/                   # Custom User model, register/login/profile, user management
│   │   ├── models.py               # Custom user with roles
│   │   ├── serializers.py
│   │   ├── views.py                # AuthViewSet, UserViewSet
│   │   ├── signals.py              # Auto-create leave balances on user creation
│   │   └── management/commands/seed_data.py
│   ├── departments/                # Department CRUD
│   ├── attendance/                 # Attendance records, check-in/out, summary
│   ├── leaves/                     # Leave types, requests, balances, review workflow
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── gunicorn.conf.py
├── frontend/                       # React app
│   ├── src/
│   │   ├── pages/                  # Login, Register, Dashboard, Attendance, Leaves, etc.
│   │   ├── components/             # Layout, UI
│   │   ├── context/AuthContext.jsx # JWT auth state
│   │   └── services/api.js         # Axios instance with token refresh
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── deployment/
│   └── nginx.conf                  # Nginx config
├── docker-compose.yml
└── README.md
```

---

## Database Design

Relational schema (ER model) with proper primary/foreign keys and normalized tables:

```
Department 1---* User  *---1 Manager(User self-ref)
User 1---* Attendance
User 1---* LeaveRequest *---1 LeaveType
User 1---* LeaveBalance *---1 LeaveType
LeaveRequest *---1 User (reviewed_by)
```

- **Department**: `id (PK)`, `name`, `code`, `description`
- **User** (custom, replaces Django's default): `id (PK)`, `username`, `email`, `role`, `department (FK)`, `manager (FK self-ref)`, `phone_number`, `avatar (image)`
- **Attendance**: `id (PK)`, `employee (FK)`, `date`, `check_in`, `check_out`, `status`, `worked_hours` (unique constraint on `employee + date`)
- **LeaveType**: `id (PK)`, `name`, `code`, `default_days`, `is_paid`
- **LeaveRequest**: `id (PK)`, `employee (FK)`, `leave_type (FK)`, `start_date`, `end_date`, `duration_days`, `status`, `reviewed_by (FK)`
- **LeaveBalance**: `id (PK)`, `employee (FK)`, `leave_type (FK)`, `allocated_days`, `used_days` (unique on `employee + leave_type`)

---

## Live Credentials (Demo Users)

The database is pre-seeded with the following demo accounts via `python manage.py seed_data`:

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| **Admin** | `admin` | `admin12345` | Full system access |
| **Manager** | `manager` | `manager12345` | Manages Engineering team |
| **Employee** | `john` | `employee12345` | Regular employee |
| **Employee** | `sara` | `employee12345` | Regular employee |
| **Employee** | `mike` | `employee12345` | Regular employee |

> **Important:** These are demo credentials only. Change them when deploying to production.

For the **Django admin portal**, use `admin / admin12345`.

---

## Installation & Setup

### Prerequisites

- Python 3.10+ (recommend 3.12)
- Node.js 18+ and npm
- (Optional, for PostgreSQL) PostgreSQL 13+
- (Optional, for Docker deployment) Docker + Docker Compose

### Option A: Quick Setup (with SQLite — recommended for first run)

**1. Create a Python virtual environment and activate it**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

**2. Install backend dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

```bash
# Copy the example env file
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

The default `.env` uses SQLite with `DEBUG=True`, which works out of the box.

**4. Run database migrations**

```bash
python manage.py migrate
```

**5. (Optional) Seed demo data — users, departments, leave types, balances, attendance**

```bash
python manage.py seed_data
```

> If you skip seeding, create a superuser with `python manage.py createsuperuser` to log in.

**6. Start the backend server**

```bash
python manage.py runserver
```

The API is now available at **http://127.0.0.1:8000/** (admin at `/admin/`).

---

### Option B: Setup with PostgreSQL

**1. Create the database**

```sql
CREATE DATABASE leave_management;
CREATE USER postgres WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE leave_management TO postgres;
```

**2. Edit `.env`** — uncomment the PostgreSQL block and comment the SQLite block:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=leave_management
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

**3. Install the PostgreSQL driver (already in requirements)**

```bash
pip install psycopg2-binary
```

**4. Migrate and seed**

```bash
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

---

### Frontend Setup

**1. Install dependencies**

```bash
cd frontend
npm install
```

**2. Run the dev server** (proxies `/api` to the backend on port 8000)

```bash
npm run dev
```

Open **http://localhost:3000** in your browser.

**3. Production build** (optional)

```bash
npm run build
```

---

## Run the Tests

Backend comes with 26 automated tests covering authentication, permissions, validation, leave-balance logic, and edge cases.

```bash
cd backend
python manage.py test core -v 2
```

Expected result: `Ran 26 tests in ...s ... OK`

---

## API Documentation

Base URL: `http://127.0.0.1:8000/api/`

Authentication: Send header `Authorization: Bearer <access_token>`.

### Auth

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/token/` | Obtain JWT (username + password) | Public |
| POST | `/api/token/refresh/` | Refresh access token | Public |
| POST | `/api/auth/register/` | Register as employee | Public |
| GET | `/api/users/me/` | Get current profile | Authenticated |
| PUT/PATCH | `/api/users/me/` | Update own profile | Authenticated |
| POST | `/api/users/change_password/` | Change password | Authenticated |

### Users

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/users/` | List users (filter by `role`, `department`) | Admin |
| POST | `/api/users/` | Create a user (any role) | Admin |
| PATCH | `/api/users/{id}/` | Update user / activate-deactivate | Admin |

### Departments

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/departments/` | List departments | Authenticated |
| POST | `/api/departments/` | Create department | Admin/Manager |
| PATCH | `/api/departments/{id}/` | Update department | Admin/Manager |
| DELETE | `/api/departments/{id}/` | Delete department | Admin/Manager |

### Attendance

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/attendance/` | List attendance (scoped by role) | Authenticated |
| GET | `/api/attendance/today/` | Today's record for current user | Authenticated |
| POST | `/api/attendance/check_in/` | Check in (auto sets late status after 09:15) | Authenticated |
| POST | `/api/attendance/check_out/` | Check out (computes worked hours) | Authenticated |
| GET | `/api/attendance/summary/` | Monthly summary (`year`, `month`) | Authenticated |

**Filtering/pagination:** `?employee=<id>&status=<status>&date=<date>&page=1&page_size=10&search=...&ordering=-date`

### Leaves

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/leaves/types/` | List leave types | Authenticated |
| POST | `/api/leaves/types/` | Create leave type | Admin/Manager |
| GET | `/api/leaves/requests/` | List requests (scoped by role) | Authenticated |
| POST | `/api/leaves/requests/` | Create a leave request (validated against balance) | Authenticated |
| POST | `/api/leaves/requests/{id}/review/` | Approve/reject (`{"status": "approved"}`) | Admin/Manager |
| POST | `/api/leaves/requests/{id}/cancel/` | Cancel pending request | Owner/Admin |
| GET | `/api/leaves/balances/` | List leave balances | Authenticated |

**Example — apply for leave:**

```bash
curl -X POST http://127.0.0.1:8000/api/leaves/requests/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": 1,
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
    "duration_days": 3,
    "reason": "Family trip"
  }'
```

**Example — review a request (manager/admin):**

```bash
curl -X POST http://127.0.0.1:8000/api/leaves/requests/1/review/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "review_note": "Approved"}'
```

---

## Authentication Flow

1. `POST /api/token/` with `username`/`password` returns `{ "access": "...", "refresh": "..." }`.
2. Send `Authorization: Bearer <access>` on all protected endpoints.
3. When the access token expires, `POST /api/token/refresh/` with `{ "refresh": "<refresh>" }` returns a new access token.
4. The React frontend automatically refreshes tokens via an Axios interceptor, so users stay logged in without manual re-authentication.

---

## Docker Deployment

The whole stack (PostgreSQL + Django backend + React frontend) can be run with Docker Compose.

```bash
# From the project root
docker-compose up --build
```

- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000**

To seed demo data inside the container, if desired:

```bash
docker-compose exec backend python manage.py seed_data
```

> For a fully working Docker demo, first seed the DB by running the migrate + seed commands manually before `docker-compose up`, or add a one-off `seed` step — the backend container runs `migrate`/`collectstatic` automatically on start.

---

## Deployment to Production

### Environment Variables (`.env`)

```env
SECRET_KEY=<long-random-string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=leave_management
DB_USER=postgres
DB_PASSWORD=<strong-password>
DB_HOST=db
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_HOST_USER=you@yourdomain.com
EMAIL_HOST_PASSWORD=<smtp-password>
```

### Steps

1. Set `DEBUG=False` and a strong `SECRET_KEY`.
2. Run migrations and collect static files:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
3. Run with **Gunicorn** (config provided in `gunicorn.conf.py`):
   ```bash
   gunicorn core.wsgi:application --config gunicorn.conf.py
   ```
4. Put **Nginx** in front using `deployment/nginx.conf` (serves the React build and proxies `/api/`, `/admin/`, `/static/`, `/media/` to Gunicorn).
5. Hardening: force `USE_TZ`, restrict `ALLOWED_HOSTS`, put `DEBUG=False`, and manage media/static volumes.

---

## Key Implementation Details

- **Custom User model** (`AUTH_USER_MODEL = 'accounts.User'`) with a `role` field enabling role-based access control (RBAC).
- **Row-level security** — even when a manager/admin can list data, the queryset is filtered so they only see records for their department/team.
- **JWT authentication** using `djangorestframework-simplejwt`, with rotating refresh tokens.
- **Leave balance logic** — validated at request time (insufficient balance → 400 error), and consumed only upon approval (wrapped in a DB transaction).
- **Signals** — automatically create leave balances for new users and for newly created leave types.
- **Query optimization** — `select_related`/`prefetch_related` used on foreign keys to avoid N+1 queries.
- **Custom exception handler** producing a consistent `{ detail, errors }` JSON envelope.
- **Custom middleware** for request logging.
- **Environment-based configuration** via `python-decouple`.
- **26 automated tests** covering unit, API, validation, authentication, and permission edge cases.

---

## License

Educational project created for the Python / Django / DRF training final assignment.
