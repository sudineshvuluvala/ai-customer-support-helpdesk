# Database Seeding & Development Fixtures

The application includes an automated database seeder (`backend/app/seed.py`) to initialize default system tables and load development demo accounts.

## Seeding Command

Run from the `backend/` directory:

```powershell
.\.venv\Scripts\flask --app run seed
```

Or to drop and recreate tables first (development only):
```powershell
.\.venv\Scripts\flask --app run seed --reset
```

## Seeded Default Accounts

All demo accounts have `is_seed=True` and an explicit `[SEED]` suffix in their name to ensure test data is never confused with genuine customer information.

| Role | Name | Email | Password |
|---|---|---|---|
| **Administrator** | Demo Admin | `admin@helpdesk.local` | `Demo@12345` |
| **Support Agent** | Demo Agent Alice | `agent1@helpdesk.local` | `Demo@12345` |
| **Support Agent** | Demo Agent Bob | `agent2@helpdesk.local` | `Demo@12345` |
| **Customer** | Demo Customer Carol | `customer1@helpdesk.local` | `Demo@12345` |
| **Customer** | Demo Customer Dave | `customer2@helpdesk.local` | `Demo@12345` |

## Included Seed Data

1. **Ticket Categories**: Technical Support, Account Issues, Billing, Product Issues, Login Problems, General Enquiries, Service Requests, Other.
2. **Knowledge Base Categories & Articles**: Getting Started, Account & Login, Billing, Attachments (grounded for AI FAQ testing).
3. **Saved Replies**: Canned greeting, info request, and closure snippets for agents.
4. **Sample Tickets**:
   - `TKT-2026-00001`: Password change issue assigned to Agent Alice with conversation & internal note.
   - `TKT-2026-00002`: Invoice query (unassigned open ticket for admin assignment testing).
   - `TKT-2026-00003`: File upload issue resolved and closed by Customer Dave.
   - `TKT-2026-00004`: Dark mode service request.
