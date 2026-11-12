import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app import create_app
from app.config import Config

app = create_app(Config)

def build_collection():
    collection = {
        "info": {
            "name": "Helpdesk AI API Collection",
            "description": "Comprehensive Postman test collection for AI-Powered Customer Support & Helpdesk Platform",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {"key": "base_url", "value": "http://127.0.0.1:5000", "type": "string"},
            {"key": "admin_token", "value": "", "type": "string"},
            {"key": "agent_token", "value": "", "type": "string"},
            {"key": "customer_token", "value": "", "type": "string"}
        ],
        "item": []
    }

    # Auth Module
    auth_folder = {
        "name": "1. Authentication",
        "item": [
            {
                "name": "Login - Admin",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status is 200', () => pm.response.to.have.status(200));",
                            "var json = pm.response.json();",
                            "if (json.data && json.data.token) { pm.collectionVariables.set('admin_token', json.data.token); }"
                        ],
                        "type": "text/javascript"
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"email": "admin@helpdesk.local", "password": "Demo@12345"})},
                    "url": {"raw": "{{base_url}}/api/v1/auth/login", "host": ["{{base_url}}"], "path": ["api", "v1", "auth", "login"]}
                }
            },
            {
                "name": "Login - Agent",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status is 200', () => pm.response.to.have.status(200));",
                            "var json = pm.response.json();",
                            "if (json.data && json.data.token) { pm.collectionVariables.set('agent_token', json.data.token); }"
                        ],
                        "type": "text/javascript"
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"email": "agent1@helpdesk.local", "password": "Demo@12345"})},
                    "url": {"raw": "{{base_url}}/api/v1/auth/login", "host": ["{{base_url}}"], "path": ["api", "v1", "auth", "login"]}
                }
            },
            {
                "name": "Login - Customer",
                "event": [{
                    "listen": "test",
                    "script": {
                        "exec": [
                            "pm.test('Status is 200', () => pm.response.to.have.status(200));",
                            "var json = pm.response.json();",
                            "if (json.data && json.data.token) { pm.collectionVariables.set('customer_token', json.data.token); }"
                        ],
                        "type": "text/javascript"
                    }
                }],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"email": "customer1@helpdesk.local", "password": "Demo@12345"})},
                    "url": {"raw": "{{base_url}}/api/v1/auth/login", "host": ["{{base_url}}"], "path": ["api", "v1", "auth", "login"]}
                }
            },
            {
                "name": "Register Customer",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"name": "New User", "email": "newuser@example.com", "password": "Password123"})},
                    "url": {"raw": "{{base_url}}/api/v1/auth/register", "host": ["{{base_url}}"], "path": ["api", "v1", "auth", "register"]}
                }
            },
            {
                "name": "Get Current User Profile (Me)",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/auth/me", "host": ["{{base_url}}"], "path": ["api", "v1", "auth", "me"]}
                }
            },
            {
                "name": "Logout Session",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/auth/logout", "host": ["{{base_url}}"], "path": ["api", "v1", "auth", "logout"]}
                }
            }
        ]
    }
    collection["item"].append(auth_folder)

    # Admin Operations
    admin_folder = {
        "name": "2. Admin Endpoints",
        "item": [
            {
                "name": "Admin Dashboard",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/admin/dashboard", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "dashboard"]}
                }
            },
            {
                "name": "List All Users",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/admin/users", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "users"]}
                }
            },
            {
                "name": "List Agents & Workload",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/admin/agents?workload=1", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "agents"], "query": [{"key": "workload", "value": "1"}]}
                }
            },
            {
                "name": "Create Support Agent",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{admin_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"name": "Agent Smith", "email": "smith@helpdesk.local", "password": "Password123"})},
                    "url": {"raw": "{{base_url}}/api/v1/admin/agents", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "agents"]}
                }
            },
            {
                "name": "Audit Logs",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/admin/audit-logs", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "audit-logs"]}
                }
            },
            {
                "name": "Reports & CSV Export",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/admin/reports", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "reports"]}
                }
            },
            {
                "name": "Get Application Settings",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/admin/settings", "host": ["{{base_url}}"], "path": ["api", "v1", "admin", "settings"]}
                }
            }
        ]
    }
    collection["item"].append(admin_folder)

    # Tickets Operations
    tickets_folder = {
        "name": "3. Ticket Management",
        "item": [
            {
                "name": "Create Ticket (Customer)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{customer_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"subject": "Payment issue with credit card", "description": "Transaction failed multiple times during checkout.", "category_id": 3, "priority": "high"})},
                    "url": {"raw": "{{base_url}}/api/v1/tickets", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets"]}
                }
            },
            {
                "name": "List Tickets",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{customer_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/tickets", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets"]}
                }
            },
            {
                "name": "Get Ticket by ID",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{customer_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1"]}
                }
            },
            {
                "name": "Assign Ticket (Admin)",
                "request": {
                    "method": "PATCH",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{admin_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"agent_id": 2, "remarks": "Assigned to Alice"})},
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1/assign", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1", "assign"]}
                }
            },
            {
                "name": "Update Ticket Status",
                "request": {
                    "method": "PATCH",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{agent_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"status": "in_progress", "remarks": "Investigating with engineering team"})},
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1/status", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1", "status"]}
                }
            },
            {
                "name": "Get Ticket History",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{customer_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1/history", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1", "history"]}
                }
            }
        ]
    }
    collection["item"].append(tickets_folder)

    # Conversation Messages
    msg_folder = {
        "name": "4. Conversation Messages",
        "item": [
            {
                "name": "Get Ticket Messages",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{customer_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1/messages", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1", "messages"]}
                }
            },
            {
                "name": "Send Public Message",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{customer_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"message_content": "Here is additional context regarding the card error.", "message_type": "public"})},
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1/messages", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1", "messages"]}
                }
            },
            {
                "name": "Send Internal Note (Agent)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{agent_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"message_content": "Staff note: Verify payment gateway logs.", "message_type": "internal"})},
                    "url": {"raw": "{{base_url}}/api/v1/tickets/1/messages", "host": ["{{base_url}}"], "path": ["api", "v1", "tickets", "1", "messages"]}
                }
            }
        ]
    }
    collection["item"].append(msg_folder)

    # AI Enhancements
    ai_folder = {
        "name": "5. AI Support Services",
        "item": [
            {
                "name": "AI FAQ Chat Assistant",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{customer_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"message": "How do I reset my account password?"})},
                    "url": {"raw": "{{base_url}}/api/v1/ai/chat", "host": ["{{base_url}}"], "path": ["api", "v1", "ai", "chat"]}
                }
            },
            {
                "name": "AI Ticket Auto-Classification",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{customer_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"subject": "Charged twice on monthly invoice", "description": "I see duplicate charges on my statement for order #401"})},
                    "url": {"raw": "{{base_url}}/api/v1/ai/classify-ticket", "host": ["{{base_url}}"], "path": ["api", "v1", "ai", "classify-ticket"]}
                }
            },
            {
                "name": "AI Agent Suggested Response",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{agent_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {"mode": "raw", "raw": json.dumps({"ticket_id": 1})},
                    "url": {"raw": "{{base_url}}/api/v1/ai/suggest-reply", "host": ["{{base_url}}"], "path": ["api", "v1", "ai", "suggest-reply"]}
                }
            },
            {
                "name": "AI Knowledge Search",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{customer_token}}"}],
                    "url": {"raw": "{{base_url}}/api/v1/ai/search-knowledge?q=password reset", "host": ["{{base_url}}"], "path": ["api", "v1", "ai", "search-knowledge"], "query": [{"key": "q", "value": "password reset"}]}
                }
            }
        ]
    }
    collection["item"].append(ai_folder)

    out_file = os.path.join(os.path.dirname(__file__), 'Helpdesk.postman_collection.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2)
    print(f"Postman collection written to {out_file}")

    # Environment
    env = {
        "name": "Helpdesk Local Environment",
        "values": [
            {"key": "base_url", "value": "http://127.0.0.1:5000", "enabled": True}
        ]
    }
    env_file = os.path.join(os.path.dirname(__file__), 'Helpdesk.postman_environment.json')
    with open(env_file, 'w', encoding='utf-8') as f:
        json.dump(env, f, indent=2)
    print(f"Postman environment written to {env_file}")

if __name__ == '__main__':
    build_collection()
