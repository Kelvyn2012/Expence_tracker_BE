# Startup Expense Tracker Monorepo

A production-grade, startup-ready Expense Tracker with Django 5 (Backend) and React + Vite (Frontend).

## Features
- **Authentication**: JWT-based auth, Email Verification, Custom User Model.
- **Expenses**: CRUD, Filtering, Pagination, Monthly Summary, CSV Export.
- **User Preferences**: Dark/Light mode persistence.
- **Security**: CORS, CSRF, Rate Limiting, Secure Headers.
- **Infrastructure**: Docker Compose, PostgreSQL.

## Prerequisites
- Docker & Docker Compose
- Make (optional)

## Quick Start

1. **Clone & Setup Environment**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env 2>/dev/null || touch frontend/.env
   ```

2. **Start Application**
   ```bash
   docker-compose up -d --build
   ```
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/api/docs/

3. **Run Migrations & Seed Data**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python scripts/seed.py
   ```
   *Creates a demo user: `demo@example.com` / `password123`*

4. **Run Tests**
   ```bash
   docker-compose exec backend pytest
   ```

## Architecture

### Backend (Django)
- `config/`: Settings split by environment.
- `apps/users`: Custom User, Auth, Email Verification.
- `apps/expenses`: Expense business logic.
- `apps/common`: Shared utilities.

### Frontend (React)
- `src/pages`: Feature pages.
- `src/components/ui`: Reusable UI components.
- `src/context`: Auth & Theme context.
- `src/hooks`: React Query hooks.

## API Documentation
Visit `http://localhost:8000/api/docs/` for Swagger UI.
