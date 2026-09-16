# Restaurant Management System

Full-stack restaurant management system.

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (JWT auth, layered routers/services/schemas)
- **Frontend:** React 19 + Vite + Tailwind CSS + React Router

## Features so far

- **Menu** — full CRUD
- **Orders** — create, list, view, advance status
- **Payments** — record and retrieve payment for an order
- **Auth** — JWT login with `admin` / `staff` roles; admin-only staff management
- Customer menu (public), staff dashboard, and admin dashboard (feature modules in progress)

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL running locally with two databases:
  - `restaurant_database`
  - `restaurant_test_database` (for tests)

## Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your values (database URLs, `SECRET_KEY`).

Create the initial admin and sample menu data:

```bash
cd backend
python seed.py
```

Default admin credentials (change via `.env`): `admin` / `admin123`

Run the API (from the `backend/` directory):

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:5173

- `/` — public customer menu
- `/login` — staff/admin login
- `/staff` — staff dashboard (requires login)
- `/admin` — admin dashboard (requires admin role)

## Tests

From the project root (backend venv active, PostgreSQL running):

```bash
pytest -q
```

## Project structure

```
backend/
  core/         # config + security (JWT, password hashing)
  database/     # engine, session, Base
  dependencies/ # auth dependencies (current user, role guards)
  models/       # SQLAlchemy models
  routers/      # API endpoints (auth, menu, orders, payments)
  schemas/      # Pydantic request/response models
  services/     # business logic
  seed.py       # bootstrap admin + sample data
frontend/
  src/
    components/ # ProtectedRoute, StaffHeader
    context/    # AuthContext
    pages/      # Login, CustomerMenu, StaffDashboard, AdminDashboard
    services/   # api.js (fetch client + auth)
tests/          # pytest suite
```
