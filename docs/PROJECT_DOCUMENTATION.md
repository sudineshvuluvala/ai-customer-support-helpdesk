# Project Documentation — AI-Powered Customer Support & Helpdesk

**Full-Stack Python Major Project Submission**
- **Backend**: Python 3.13, Flask 3.1, SQLAlchemy 2.0 ORM, Flask-Migrate (Alembic)
- **Database**: MySQL 8.0 (InnoDB, utf8mb4)
- **Frontend**: React 19, JavaScript ESNext, Bootstrap 5, Vite 8, React Router 7
- **Deployment Platform**: AWS EC2, Gunicorn, Nginx, HTTPS (Let's Encrypt), ap-southeast-2

---

## 1. Project Introduction
The **AI-Powered Customer Support & Helpdesk** is an enterprise-grade customer communication and ticket resolution platform. It centralizes incoming customer requests, coordinates support agent assignment, enforces Service Level Agreements (SLA), maintains conversation history, and provides AI-powered assistance to automate repetitive queries while ensuring human oversight on all customer-facing replies.

## 2. Problem Statement
Traditional customer support operations suffer from fragmented email exchanges, lack of ownership tracking, delayed first-response times, and repetitive inquiries that overwhelm human agents. Without a centralized platform, tracking resolution times and maintaining audit compliance is error-prone.

## 3. Project Objectives
- Centralize multi-channel customer inquiries into traceable, unique ticket records.
- Implement strict three-tier Role-Based Access Control (Admin, Agent, Customer).
- Maintain complete chronological conversation histories with protected internal notes.
- Integrate progressive AI enhancements for 24/7 FAQ answering, ticket classification, and suggested agent responses.
- Enforce Service Level Agreements (SLA) with real-time breach indicators.
- Provide secure file attachment management with magic-byte content validation.

## 4. Project Scope
The application encompasses a customer portal, an agent workspace, an administrative governance center, an integrated knowledge base, background notification dispatch, and operational analytics. It is designed for single-server or distributed AWS cloud environments.

## 5. Functional Requirements
- **Authentication**: JWT token-based authentication with expiration and server-side token revocation on logout.
- **Ticket Lifecycle**: Creation, auto-numbering (`TKT-YYYY-XXXXX`), status transitions, priority management, agent assignment, and customer closure.
- **Messaging**: Public replies between customer and staff; staff-only internal notes.
- **File Management**: Whitelisted upload validation, unique UUID on-disk storage, and role-authorized downloads.
- **Knowledge Base**: Category management, article authoring, draft/published statuses, and full-text search.
- **AI Services**: Grounded FAQ answering via knowledge articles, ticket category/priority suggestions, and agent draft reply generation.

## 6. Non-Functional Requirements
- **Security**: Cryptographic password hashing (scrypt/pbkdf2), SQL injection prevention via ORM parameterization, XSS mitigation, and PII masking.
- **Performance**: Sub-100ms API response times on indexed relational queries; asynchronous email dispatch.
- **Reliability**: Graceful fallback to local heuristics and BM25 search if external AI services are unavailable.
- **Responsiveness**: Mobile, tablet, and desktop adaptive layouts using Bootstrap 5 and flexbox grid systems.

## 7. User Roles & Permission Matrix
| Capability | Admin | Support Agent | Customer |
|---|:---:|:---:|:---:|
| Register Account | ❌ | ❌ | ✅ |
| Create Support Ticket | ✅ | ❌ | ✅ |
| View Own Tickets | ✅ | ✅ (Assigned) | ✅ (Self only) |
| View All Tickets | ✅ | ❌ | ❌ |
| Assign / Reassign Agent | ✅ | ❌ | ❌ |
| Update Status to In-Progress | ✅ | ✅ | ❌ |
| Resolve Ticket | ✅ | ✅ | ❌ |
| Close / Reopen Ticket | ✅ | ❌ | ✅ |
| Post Internal Note | ✅ | ✅ | ❌ |
| Upload Attachments | ✅ | ✅ | ✅ |
| Delete Own Attachments | ✅ | ✅ | ✅ |
| Manage Categories | ✅ | ❌ | ❌ |
| Publish KB Articles | ✅ | ❌ | ❌ |
| Read Published KB | ✅ | ✅ | ✅ |
| Access AI FAQ Assistant | ✅ | ✅ | ✅ |
| AI Suggested Replies | ✅ | ✅ | ❌ |
| Access Analytics & Reports | ✅ | ✅ (Limited) | ❌ |
| Modify System Settings | ✅ | ❌ | ❌ |

## 8. Technology Stack
- **Backend API**: Flask 3.1.0, Werkzeug, PyJWT, Flask-CORS, Flask-Limiter.
- **Database & ORM**: MySQL Server 8.0, PyMySQL, SQLAlchemy 2.0, Flask-Migrate.
- **Frontend SPA**: React 19, Vite 8, React Router 7, Bootstrap 5.3, Bootstrap Icons.
- **Production Server**: Gunicorn WSGI, Nginx HTTP/HTTPS reverse proxy, Systemd.
- **Cloud & OS**: AWS EC2, Ubuntu 22.04 LTS, Region `ap-southeast-2`.

## 9. System & Deployment Architecture
Detailed architecture diagrams and flowcharts are provided in [`docs/architecture.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/architecture.md).

## 10. Database Architecture & ER Diagram
Full entity relationships, constraints, and index definitions are documented in [`docs/er-diagram.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/er-diagram.md) and [`database/schema.sql`](file:///c:/Users/sudin/Desktop/fullstackproject/database/schema.sql).

## 11. REST API Specification
Every API endpoint is accessible under `/api/v1/`:
- **Auth**: `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`.
- **Users**: `GET /users`, `GET /users/profile`, `PUT /users/profile`, `GET /users/<id>`.
- **Admin**: `GET /admin/dashboard`, `GET /admin/users`, `POST /admin/users`, `GET /admin/agents`, `POST /admin/agents`, `GET /admin/tickets`, `GET /admin/reports`, `GET /admin/audit-logs`, `GET/PUT /admin/settings`.
- **Tickets**: `POST /tickets`, `GET /tickets`, `GET /tickets/<id>`, `PUT /tickets/<id>`, `PATCH /tickets/<id>/status`, `PATCH /tickets/<id>/priority`, `PATCH /tickets/<id>/assign`, `GET /tickets/<id>/history`.
- **Messages**: `GET /tickets/<id>/messages`, `POST /tickets/<id>/messages`.
- **Attachments**: `POST /tickets/<id>/attachments`, `GET /tickets/<id>/attachments`, `GET /attachments/<id>/download`, `DELETE /attachments/<id>`.
- **Categories**: `GET/POST /categories`, `PUT/DELETE /categories/<id>`.
- **Knowledge Base**: `GET/POST /knowledge/articles`, `GET/PUT/DELETE /knowledge/articles/<id>`, `GET/POST /knowledge/categories`.
- **AI**: `POST /ai/chat`, `POST /ai/classify-ticket`, `POST /ai/suggest-reply`, `GET /ai/search-knowledge`.
- **Notifications**: `GET /notifications`, `PATCH /notifications/<id>/read`, `PATCH /notifications/read-all`.
- **Analytics**: `GET /analytics`, `GET /analytics/tickets`, `GET /analytics/agents`, `GET /analytics/sla`.

## 12. Complete Support Ticket Workflow
1. **Creation**: Customer inputs subject, description, category, and priority. Unique number `TKT-YYYY-XXXXX` allocated.
2. **Assignment**: Administrator views unassigned queue, inspects agent workload, and assigns ticket to an active agent.
3. **Notification**: Agent receives notification; ticket status moves to `Assigned`.
4. **Investigation**: Agent inspects details, reads attachments, and posts public reply or internal staff note. First response timestamp recorded for SLA. Status transitions to `In Progress`.
5. **Customer Feedback**: If waiting for information, agent flags `Waiting for Customer`. Customer reply automatically re-activates ticket to `In Progress`.
6. **Resolution**: Agent resolves ticket. SLA marks as `Met` or `Breached`.
7. **Closure**: Customer reviews resolution and closes ticket, or it auto-closes after configured days.

## 13. File Upload & Attachment Security
Uploaded files are validated against allowed MIME types and magic-byte signatures. Files are assigned randomized UUID names on disk and stored in `app/uploads/` outside public web server roots. Direct public URL access is blocked in Nginx (`location /uploads/ { deny all; }`). Downloads are streamed through authenticated endpoints after verifying ticket participation.

## 14. Knowledge Base & Grounded AI FAQ
Articles can be authored in Draft, Published, or Archived states. Only published articles are exposed to customers and indexed by the AI engine. The AI FAQ assistant uses a retrieval-augmented generation (RAG) approach: relevant article snippets are extracted via BM25 keyword matching and injected into LLM context tags. If no matching articles exist, the assistant politely declines to guess and prompts the user to open a support ticket.

## 15. Testing & Quality Assurance
The backend test suite (`pytest`) contains 41 comprehensive tests covering authentication, RBAC authorization, workflow state machines, attachment validation, SLA recomputations, and AI fallbacks. All 41 tests pass consistently. The frontend includes automated production builds with Vite.

## 16. Known Limitations
- External AI API keys (Gemini / OpenAI) require user environment variable configuration; local heuristics and BM25 search act as the default fallback.
- In-memory rate limiting operates per-worker process in development; Redis is recommended for distributed multi-server clusters.
- Real SMTP email dispatch requires setting valid mail server credentials in `.env`.
