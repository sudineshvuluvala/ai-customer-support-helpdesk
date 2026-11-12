# Viva Preparation & Architectural Defense Guide

This document prepares the developer to explain and defend every design decision, security control, and code component implemented in the **AI-Powered Customer Support & Helpdesk** during academic viva and technical evaluations.

---

## 1. Core Architecture & Technologies

### Q: Why did you choose a Modular Monolith architecture instead of Microservices?
**Defense:**
For a customer support platform of this scope, a modular monolith implemented with Flask Blueprints and layered services provides high cohesion and low cognitive overhead without the operational complexity (service mesh, network latency, distributed transactions) of microservices. Each domain (`tickets`, `users`, `knowledge`, `ai`) has its own routes and service layer, allowing simple refactoring into microservices in the future if required.

### Q: How do the Frontend and Backend communicate?
**Defense:**
Communication is completely decoupled via asynchronous REST APIs over JSON. The React SPA never receives pre-rendered server templates. Requests are authenticated using HTTP Bearer JWT tokens in the `Authorization` header (`services/api.js`). Responses follow a standardized JSON envelope structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional user-friendly message",
  "pagination": { "page": 1, "per_page": 10, "total": 45, "pages": 5 }
}
```

---

## 2. Database Schema & Data Modeling

### Q: Explain the Database Schema and Foreign Key Constraints.
**Defense:**
The schema consists of 12 relational tables hosted on MySQL (`InnoDB`):
- `users`: Core identity table with `role` and `account_status` enums.
- `tickets`: Central entity containing `customer_id` and `assigned_agent_id` (foreign keys to `users`), plus `category_id` (foreign key to `ticket_categories`).
- `ticket_messages`: Message thread records linked to `tickets` and `users`.
- `ticket_attachments`: File metadata linking tickets, messages, and uploaders.
- `ticket_status_history`: Immutable audit trail recording old vs new states with timestamps and actor IDs.
- `sla_records`: 1-to-1 relationship with `tickets` storing target deadlines and breach states.

### Q: How do you prevent race conditions when creating unique ticket numbers?
**Defense:**
In `ticket_service.py:create_ticket`, the ticket is initially saved with a temporary identifier. After `db.session.flush()`, the database allocates an auto-incrementing integer `ticket_id`. The application formats the deterministic number `TKT-{YYYY}-{ticket_id:05d}` and commits the transaction. This guarantees zero duplicates without table locking.

---

## 3. Security Implementation & RBAC

### Q: How do you enforce Role-Based Access Control?
**Defense:**
We never rely on frontend visual hiding alone. Every protected API endpoint is guarded on the backend by `@roles_required(*roles)` (`app/utils/permissions.py`). If a customer attempts to query `/api/v1/admin/dashboard`, the decorator decodes the JWT payload, inspects the role, and immediately returns HTTP 403 Forbidden.

### Q: How do you prevent horizontal privilege escalation (e.g. Customer A reading Customer B's ticket)?
**Defense:**
Through the central verification utility `get_ticket_for_user(ticket_id, user)` in `ticket_service.py`. If a customer requests a ticket ID that does not match their `user_id`, or if an agent requests a ticket not assigned to them, the system returns HTTP 404 Not Found (rather than 403) to prevent attacker ID enumeration.

### Q: How do you protect file uploads against malicious executable scripts?
**Defense:**
In `app/utils/file_helpers.py:validate_upload`:
1. We enforce an allowed whitelist (`.pdf`, `.png`, `.jpg`, `.txt`, `.docx`).
2. We inspect real file magic bytes (e.g., verifying `b'%PDF-'` for PDF or `b'\x89PNG\r\n\x1a\n'` for PNG). A renamed `.exe` or `.php` file fails content verification.
3. Stored filenames are replaced with cryptographic random UUIDs (`uuid4().hex`) and stored in a private directory outside Nginx's static web root. Downloads require authenticated API calls.

---

## 4. AI Enhancement Services & Safety

### Q: How is AI integrated, and what happens if the AI service goes down?
**Defense:**
AI functionality is treated as an optional, progressive enhancement in `app/ai/`. The application uses an adapter pattern supporting Gemini and OpenAI-compatible endpoints. If an API key is missing or the external provider fails with a timeout:
- The FAQ assistant gracefully falls back to local BM25 ranking over published articles (`knowledge_search.py`).
- Ticket auto-classification falls back to a rule-based keyword heuristic.
- Agent response suggestions fall back to structured templates citing matching articles.
- The core helpdesk ticketing workflows never crash.

### Q: How do you prevent Prompt Injection and Data Leakage?
**Defense:**
In `app/ai/safety_checks.py`:
1. Customer inputs are sanitized using regular expressions that redact credit card numbers, email addresses, and phone numbers before routing queries to external LLMs.
2. System prompts enforce strict grounding tags: `<context>...</context>`.
3. If an input attempts prompt injection (e.g. "Ignore previous instructions"), the request is rejected and redirected to local article matching.

---

## 5. Service Level Agreements (SLA) & Lifecycle

### Q: How is SLA compliance calculated and monitored?
**Defense:**
In `sla_service.py`, each priority level has configurable targets for first response and resolution (e.g., Critical: 1hr response / 4hr resolution). When a ticket is created:
1. `response_due_at` and `resolution_due_at` are calculated.
2. When an agent submits their first public reply, `first_response_at` is locked.
3. If the remaining window drops under 25% of the total target, status becomes `at_risk`. If deadlines expire without resolution, it transitions to `breached`.

---

## 6. AWS Production Deployment

### Q: Describe your AWS EC2 and Nginx configuration.
**Defense:**
- **Nginx** acts as the public edge server handling HTTPS (TLS 1.2/1.3) via Let's Encrypt Certbot.
- Static React files (`frontend/dist`) are served directly by Nginx with high caching efficiency.
- API traffic (`/api/*`) is reverse-proxied over port 8000 to **Gunicorn**, which manages 4 worker processes.
- **MySQL** runs in a private subnet with security groups configured so that port 3306 only accepts inbound connections from the app security group.
