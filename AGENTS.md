# AGENTS.md — Development Guidelines for AI Assistants

This repository houses the **AI-Powered Customer Support & Helpdesk** full-stack application built with Flask (Python 3.13), MySQL (relational database), and React (Vite SPA).

## 1. Project Organization
- `backend/`: Flask REST API modular monolith (Application Factory in `app/__init__.py`).
  - `app/models/`: SQLAlchemy 2.0 ORM models.
  - `app/routes/`: Blueprint endpoint handlers registered with `/api/v1`.
  - `app/services/`: Pure business logic, status transitions, SLA calculations, and audit triggers.
  - `app/ai/`: Grounded RAG FAQ assistant, heuristic & LLM classifier, response suggestions.
  - `app/tests/`: Pytest suite (run with `backend\.venv\Scripts\python -m pytest`).
- `frontend/`: React 19 SPA configured with Vite and React Router 7.
  - `src/components/`: Reusable accessible UI components (DataTable, Modal, FileUpload, ChatMessage).
  - `src/pages/`: Role-segregated views (`admin/`, `agent/`, `customer/`, `shared/`).
  - `src/services/`: Centralized API clients using native `fetch`.
  - `src/context/`: AuthContext managing JWT token lifecycle.
- `database/`: `schema.sql`, `generate_schema.py`, and least-privilege SQL scripts.
- `deployment/`: Gunicorn, Nginx, Systemd, automated backup, and AWS documentation.
- `docs/`: ER diagrams, system architecture, viva notes, and comprehensive technical specifications.
- `postman/`: Postman collection and environment for API regression testing.

## 2. Coding & Security Rules
- **No SQLite in Production**: Production uses MySQL with `InnoDB` and `utf8mb4`. SQLite is reserved for in-memory Pytest execution.
- **Backend Authorization**: Never trust frontend routing. Every protected endpoint must declare `@login_required` or `@roles_required('admin', 'agent')`.
- **Ownership Verification**: All ticket operations must pass through `get_ticket_for_user(ticket_id, user)` in `ticket_service.py` to prevent horizontal privilege escalation.
- **File Upload Security**: Validate real magic bytes before accepting files. Store files with random UUIDs outside web root.
- **Database Seeding**: Development demo accounts must have `is_seed=True` and an explicit `[SEED]` suffix.
