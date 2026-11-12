# AI-Powered Customer Support & Helpdesk

A complete, enterprise-grade, responsive full-stack Python web application designed for modern customer care operations. Built with Flask, MySQL, React.js, Bootstrap 5, and progressive AI enhancements.

---

## 🌟 Key Features

- **Three Role-Based Portals**:
  - **Administrator**: Comprehensive system oversight, agent workload management, ticket routing, category management, knowledge base publishing, SLA monitoring, audit trails, and data export.
  - **Support Agent**: Focused ticket queue, two-way customer messaging, private internal staff notes, canned saved replies, and AI-assisted reply drafting.
  - **Customer**: Clean support ticket creation, real-time ticket status tracking, interactive conversation history, secure attachment uploads, 24/7 AI FAQ assistant, and searchable knowledge base.
- **Support Ticket Lifecycle**: Automated unique ticket numbering (`TKT-YYYY-XXXXX`), rule-enforced status transitions, priority escalation, and customer resolution verification.
- **Service Level Agreement (SLA) Tracking**: Configurable response and resolution windows by priority, real-time "at risk" and "breached" indicators, and compliance metrics.
- **Secure Attachment Handling**: Whitelist file validation with real magic-byte inspection (PDF, PNG, JPG, TXT, DOCX), randomized UUID storage outside public web roots, and authenticated streaming downloads.
- **Progressive AI Enhancements**:
  - Grounded Conversational FAQ Assistant (RAG backed by published knowledge base articles).
  - Ticket Category & Priority Auto-Classification.
  - Agent Response Generator (Draft suggestions requiring explicit agent review and approval).
  - Local BM25 and heuristic fallback ensuring the application functions 100% offline without external AI keys.
- **Security & Integrity**: JWT session authentication, password hashing with scrypt/pbkdf2, server-side token revocation on logout, rate limiting, and backend RBAC on all endpoints.

---

## 🛠️ Mandatory Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Backend Framework** | Python 3.13 / Flask 3.1 | Application factory pattern, Flask Blueprints, Flask-CORS, Flask-Limiter |
| **Database & ORM** | MySQL 8.0 / SQLAlchemy 2.0 | Relational database, foreign keys, transactions, indexes, PyMySQL, Flask-Migrate |
| **Frontend Framework** | React 19 / Vite 8 | Single Page Application (SPA), React Router 7, Context API, pure REST client |
| **Styling & UI** | Bootstrap 5.3 / CSS3 | Responsive dashboard layouts, mobile collapsible sidebars, Bootstrap Icons |
| **Testing** | Pytest 8.0 / Vitest | 41 backend automated test cases covering authentication, RBAC, workflows, and AI |
| **Production Server** | Gunicorn / Nginx | WSGI process manager, HTTP/HTTPS reverse proxy, Let's Encrypt TLS |
| **Cloud Deployment** | AWS EC2 (ap-southeast-2) | Systemd daemon, automated daily MySQL backups, production environment configs |

---

## 🏗️ System Architecture

```
React Frontend (Vite SPA) ──[HTTPS / REST API]──> Nginx (Port 80/443)
                                                        │
                                                        ▼
                                             Gunicorn WSGI (127.0.0.1:8000)
                                                        │
                                                        ▼
                                             Flask Backend Application
                                              ├── Auth & RBAC Middleware
                                              ├── REST API Blueprints
                                              ├── Service Logic Layer
                                              └── AI Subsystem (Grounded RAG)
                                                        │
                              ┌─────────────────────────┴────────────────────────┐
                              ▼                                                  ▼
                   MySQL Database Engine                               Protected File Storage
                 (customer_support_db)                                 (backend/app/uploads/)
```

*For complete architecture diagrams and workflows, see [`docs/architecture.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/architecture.md) and [`docs/er-diagram.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/er-diagram.md).*

---

## 💻 Local Development Setup (Windows PowerShell)

### Prerequisites
- Python 3.10+ installed and on `PATH`
- Node.js 18+ and npm installed and on `PATH`
- MySQL Server 8.0 installed (or run with default SQLite in-memory mode for rapid testing)

### 1. Backend Setup
```powershell
cd backend

# Create virtual environment & activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
Copy-Item .env.example .env

# Run automated development seed data (initializes users, categories, sample tickets)
$env:DATABASE_URL="sqlite:///dev.db" # Or configure your MySQL credentials in .env
flask --app run seed

# Start Flask development API server (runs on http://127.0.0.1:5000)
python run.py
```

### 2. Frontend Setup
In a new terminal:
```powershell
cd frontend

# Install Node modules
npm install

# Start Vite development server (runs on http://localhost:5173)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔑 Development Demo Credentials

| Role | Email | Password | Access Scope |
|---|---|---|---|
| **Administrator** | `admin@helpdesk.local` | `Demo@12345` | Complete platform management, users, tickets, SLA, settings |
| **Support Agent** | `agent1@helpdesk.local` | `Demo@12345` | Assigned ticket queue, replies, internal notes, saved snippets |
| **Support Agent** | `agent2@helpdesk.local` | `Demo@12345` | Assigned ticket queue, replies, internal notes, saved snippets |
| **Customer** | `customer1@helpdesk.local` | `Demo@12345` | Ticket creation, personal ticket tracking, AI FAQ assistant |
| **Customer** | `customer2@helpdesk.local` | `Demo@12345` | Ticket creation, personal ticket tracking, AI FAQ assistant |

---

## 🧪 Testing & Quality Assurance

### Run Backend Automated Tests (Pytest)
```powershell
cd backend
.\.venv\Scripts\python -m pytest -v
```
*Executes all 41 unit, integration, and security tests across authentication, RBAC authorization, ticket state machines, attachment security, and AI provider fallbacks.*

### Run Frontend Production Build Check
```powershell
cd frontend
npm run build
```

---

## 🚀 AWS EC2 Production Deployment

The project is fully pre-configured for deployment on **AWS EC2 (ap-southeast-2 - Sydney)**:
- **Gunicorn WSGI Configuration**: [`deployment/gunicorn.conf.py`](file:///c:/Users/sudin/Desktop/fullstackproject/deployment/gunicorn.conf.py)
- **Nginx Reverse Proxy & SSL**: [`deployment/nginx.conf`](file:///c:/Users/sudin/Desktop/fullstackproject/deployment/nginx.conf)
- **Systemd Service**: [`deployment/helpdesk.service`](file:///c:/Users/sudin/Desktop/fullstackproject/deployment/helpdesk.service)
- **Automated EC2 Provisioning Script**: [`deployment/setup_ec2.sh`](file:///c:/Users/sudin/Desktop/fullstackproject/deployment/setup_ec2.sh)
- **MySQL Backup Script**: [`deployment/mysql_backup.sh`](file:///c:/Users/sudin/Desktop/fullstackproject/deployment/mysql_backup.sh)
- **Comprehensive AWS Deployment Guide**: [`deployment/AWS_DEPLOYMENT.md`](file:///c:/Users/sudin/Desktop/fullstackproject/deployment/AWS_DEPLOYMENT.md)

*Live Deployment Status*: **Ready for provisioning** (deployment files prepared; waiting for user cloud authorization).

---

## 📚 Complete Project Documentation

- [`docs/PROJECT_DOCUMENTATION.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/PROJECT_DOCUMENTATION.md): Complete 16-section major project report.
- [`docs/er-diagram.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/er-diagram.md): Complete Mermaid ER diagram and table schemas.
- [`docs/architecture.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/architecture.md): High-level system topology and AWS flowcharts.
- [`docs/VIVA_GUIDE.md`](file:///c:/Users/sudin/Desktop/fullstackproject/docs/VIVA_GUIDE.md): Technical defense questions and architectural rationales for project viva.
- [`postman/Helpdesk.postman_collection.json`](file:///c:/Users/sudin/Desktop/fullstackproject/postman/Helpdesk.postman_collection.json): Automated Postman test collection covering all registered REST APIs.
