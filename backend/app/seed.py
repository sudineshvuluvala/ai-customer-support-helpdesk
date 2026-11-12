"""Development seed data. Every seeded account has is_seed=True and an obvious '[SEED]' name suffix -
this is NOT real customer information."""
import os
from datetime import datetime, timedelta

from .extensions import db
from .models import (KnowledgeArticle, KnowledgeCategory, SavedReply, Ticket, TicketCategory, User)
from .services import assignment_service, auth_service, conversation_service as cs, sla_service, ticket_service as ts

DEFAULT_CATEGORIES = [
    ("Technical Support", "Errors, bugs and technical problems"),
    ("Account Issues", "Profile, verification and account settings"),
    ("Billing", "Invoices, payments and subscriptions"),
    ("Product Issues", "Problems with a product or its features"),
    ("Login Problems", "Cannot sign in, password reset, locked accounts"),
    ("General Enquiries", "General questions and information"),
    ("Service Requests", "Requests for new services or changes"),
    ("Other", "Anything else"),
]

KB = {
    "Getting Started": [
        ("How to create a support ticket", "To create a support ticket, log in and open Create Ticket. Enter a clear subject, describe the issue, choose a category and priority, and optionally attach screenshots or documents. After submitting you receive a unique ticket number such as TKT-2026-00001 that you can use to track progress."),
        ("Tracking the status of your ticket", "Open My Tickets to see every ticket you created. A ticket moves through Open, Assigned, In Progress, Waiting for Customer, Resolved and Closed. You receive an in-app notification whenever the status changes or an agent replies."),
    ],
    "Account & Login": [
        ("How to reset your password", "If you forgot your password, create a ticket in the Login Problems category and an agent will help you regain access. If you are logged in, you can change your password at any time from your Profile page by entering your current password and a new one with at least 8 characters including letters and digits."),
        ("Why is my account locked or deactivated", "Accounts may be deactivated by an administrator. If you cannot log in and see that your account has been deactivated, please contact support by creating a ticket from another account or by contacting the administrator directly."),
    ],
    "Billing": [
        ("Where to find your invoices", "Invoices and billing questions are handled by our billing team. Create a ticket in the Billing category and include the invoice period you are asking about. Agents can only answer using information available in your ticket; this article does not describe any refund policy."),
    ],
    "Attachments": [
        ("Supported attachment types and size limit", "You can attach PDF, PNG, JPG, JPEG, TXT and DOCX files to a ticket or a reply. Each file must be 5 MB or smaller. Files are checked when uploaded and only you and the support team assigned to your ticket can download them."),
    ],
}

SAVED = [
    ("Greeting", "Hi, thank you for contacting support. I'm happy to help with this."),
    ("Need more information", "Could you please share more details such as the exact error message, the time it happened and any screenshots?"),
    ("Resolved - closing", "I'm glad we could resolve this. If everything looks good on your side, you can close the ticket. Feel free to reply if you need further help."),
]


def seed_database(password=None):
    password = password or os.getenv("SEED_PASSWORD", "Demo@12345")
    if User.query.filter_by(email="admin@helpdesk.local").first():
        return "Seed data already present - nothing changed."

    for name, desc in DEFAULT_CATEGORIES:
        if not TicketCategory.query.filter_by(category_name=name).first():
            db.session.add(TicketCategory(category_name=name, description=desc))
    sla_service.update_settings(sla_service.DEFAULT_SETTINGS)
    db.session.flush()

    def mk(name, email, role):
        u = auth_service.register_user(f"{name} [SEED]", email, password, role=role, is_seed=True)
        return u

    admin = mk("Demo Admin", "admin@helpdesk.local", "admin")
    agent1 = mk("Demo Agent Alice", "agent1@helpdesk.local", "agent")
    agent2 = mk("Demo Agent Bob", "agent2@helpdesk.local", "agent")
    cust1 = mk("Demo Customer Carol", "customer1@helpdesk.local", "customer")
    cust2 = mk("Demo Customer Dave", "customer2@helpdesk.local", "customer")

    for cname, arts in KB.items():
        kc = KnowledgeCategory(category_name=cname)
        db.session.add(kc)
        db.session.flush()
        for title, content in arts:
            db.session.add(KnowledgeArticle(category_id=kc.category_id, title=title, content=content, status="published", created_by=admin.user_id))
    for t, c in SAVED:
        db.session.add(SavedReply(created_by=agent1.user_id, title=t, reply_content=c))
        db.session.add(SavedReply(created_by=agent2.user_id, title=t, reply_content=c))
    db.session.flush()

    cats = {c.category_name: c.category_id for c in TicketCategory.query.all()}
    samples = [
        (cust1, "Cannot log in after password change", "I changed my password yesterday and now the login page says invalid credentials.", "Login Problems", "high"),
        (cust1, "Question about invoice for last month", "Where can I download the invoice for last month? I cannot find it anywhere.", "Billing", "medium"),
        (cust2, "App crashes when uploading a file", "Every time I upload a PNG the application shows an error and closes. This is blocking my work.", "Technical Support", "critical" if False else "high"),
        (cust2, "Feature request: dark mode", "It would be great to have a dark mode option in the dashboard.", "Service Requests", "low"),
    ]
    tickets = [ts.create_ticket(c, s, d, cats[cat], p) for c, s, d, cat, p in samples]
    db.session.flush()
    assignment_service.assign_ticket(tickets[0], agent1.user_id, admin)
    assignment_service.assign_ticket(tickets[2], agent2.user_id, admin)
    cs.add_message(tickets[0], agent1, "Hi Carol, could you tell us which browser you are using? Please also try the reset flow.")
    cs.add_message(tickets[0], agent1, "Customer may have a stale cached session - ask to clear cookies.", "internal")
    cs.add_message(tickets[0], cust1, "I am using Chrome on Windows. Clearing cookies did not help.")
    cs.add_message(tickets[2], agent2, "Thanks Dave, we are reproducing this issue now.")
    ts.change_status(tickets[2], "resolved", agent2, "Fixed in latest release")
    ts.change_status(tickets[2], "closed", cust2, "Confirmed fixed")
    # backdate a few tickets so analytics trends/SLA show variety
    for i, t in enumerate(tickets):
        t.created_at = datetime.utcnow() - timedelta(days=(len(tickets) - i) * 2, hours=3)
        sla_service.recompute_due_dates(t)
    tickets[2].resolved_at = tickets[2].created_at + timedelta(hours=6)
    tickets[2].closed_at = tickets[2].resolved_at + timedelta(hours=2)
    if tickets[2].sla:
        tickets[2].sla.resolved_at = tickets[2].resolved_at
    db.session.commit()
    return f"Seeded 5 users (password: {password}), categories, knowledge base, saved replies and 4 tickets."
