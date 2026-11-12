from .conftest import new_ticket, upload


def _agent_id(client, headers):
    return client.get("/api/v1/auth/me", headers=headers).get_json()["data"]["user_id"]


def test_full_ticket_workflow(client, admin, agent1, cust1):
    r = new_ticket(client, cust1)
    assert r.status_code == 201
    t = r.get_json()["data"]
    tid = t["ticket_id"]
    import re
    assert re.fullmatch(r"TKT-\d{4}-\d{5}", t["ticket_number"]) and t["status"] == "open"
    assert t["sla"]["response_due_at"]

    # admin sees unassigned ticket, assigns it
    un = client.get("/api/v1/admin/tickets?unassigned=1", headers=admin).get_json()["data"]
    assert tid in [x["ticket_id"] for x in un]
    aid = _agent_id(client, agent1)
    r = client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": aid}, headers=admin)
    assert r.status_code == 200 and r.get_json()["data"]["status"] == "assigned"
    notes = client.get("/api/v1/notifications", headers=agent1).get_json()
    assert any(n["related_ticket_id"] == tid and n["notification_type"] == "ticket_assigned" for n in notes["data"])

    # agent replies -> in progress + customer notified, first response SLA recorded
    r = client.post(f"/api/v1/tickets/{tid}/messages", json={"message_content": "Please unplug it."}, headers=agent1)
    assert r.status_code == 201
    d = client.get(f"/api/v1/tickets/{tid}", headers=cust1).get_json()["data"]
    assert d["status"] == "in_progress" and d["sla"]["first_response_at"]
    cn = client.get("/api/v1/notifications", headers=cust1).get_json()
    assert any(n["notification_type"] == "agent_reply" and n["related_ticket_id"] == tid for n in cn["data"]) and cn["unread_count"] > 0

    # agent sets waiting; customer reply moves it back
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "waiting_for_customer"}, headers=agent1).status_code == 200
    client.post(f"/api/v1/tickets/{tid}/messages", json={"message_content": "Done, still smoking."}, headers=cust1)
    assert client.get(f"/api/v1/tickets/{tid}", headers=cust1).get_json()["data"]["status"] == "in_progress"

    # resolve, customer closes
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "resolved"}, headers=agent1).status_code == 200
    d = client.get(f"/api/v1/tickets/{tid}", headers=cust1).get_json()["data"]
    assert d["resolved_at"] and d["sla"]["sla_status"] == "met"
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "closed"}, headers=cust1).status_code == 200
    d = client.get(f"/api/v1/tickets/{tid}", headers=cust1).get_json()["data"]
    assert d["closed_at"]

    # history retained
    hist = client.get(f"/api/v1/tickets/{tid}/history", headers=cust1).get_json()["data"]
    statuses = [(h["old_value"], h["new_value"]) for h in hist if h["event_type"] == "status"]
    assert ("open", "assigned") in statuses and ("resolved", "closed") in statuses
    assert any(h["event_type"] == "assignment" for h in hist)
    # closed ticket rejects new messages
    assert client.post(f"/api/v1/tickets/{tid}/messages", json={"message_content": "hello?"}, headers=cust1).status_code == 409


def test_customer_cannot_access_other_customers_tickets(client, cust1, cust2, admin):
    tid = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    assert client.get(f"/api/v1/tickets/{tid}", headers=cust2).status_code == 404
    assert client.get(f"/api/v1/tickets/{tid}/messages", headers=cust2).status_code == 404
    assert client.post(f"/api/v1/tickets/{tid}/messages", json={"message_content": "hi"}, headers=cust2).status_code == 404
    assert client.get(f"/api/v1/tickets/{tid}/attachments", headers=cust2).status_code == 404
    assert client.get(f"/api/v1/tickets/{tid}/history", headers=cust2).status_code == 404
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "closed"}, headers=cust2).status_code == 404
    ids = [t["ticket_id"] for t in client.get("/api/v1/tickets", headers=cust2).get_json()["data"]]
    assert tid not in ids


def test_agent_only_sees_assigned_tickets(client, agent1, agent2, admin):
    ids1 = {t["ticket_id"] for t in client.get("/api/v1/agents/tickets", headers=agent1).get_json()["data"]}
    ids2 = {t["ticket_id"] for t in client.get("/api/v1/agents/tickets", headers=agent2).get_json()["data"]}
    assert ids1 and ids2 and not (ids1 & ids2)
    other = next(iter(ids2))
    assert client.get(f"/api/v1/tickets/{other}", headers=agent1).status_code == 404
    assert client.patch(f"/api/v1/tickets/{other}/priority", json={"priority": "low"}, headers=agent1).status_code == 404


def test_assignment_rules(client, admin, agent1, agent2, cust1):
    tid = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    a1, a2 = _agent_id(client, agent1), _agent_id(client, agent2)
    assert client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": a1}, headers=agent1).status_code == 403
    assert client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": 99999}, headers=admin).status_code == 422
    cust_id = client.get("/api/v1/auth/me", headers=cust1).get_json()["data"]["user_id"]
    assert client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": cust_id}, headers=admin).status_code == 422
    assert client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": a1}, headers=admin).status_code == 200
    assert client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": a1}, headers=admin).status_code == 409
    # reassign
    r = client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": a2}, headers=admin)
    assert r.status_code == 200 and r.get_json()["data"]["assigned_agent"]["user_id"] == a2
    assert client.get(f"/api/v1/tickets/{tid}", headers=agent1).status_code == 404
    assert client.get(f"/api/v1/tickets/{tid}", headers=agent2).status_code == 200
    # inactive agent cannot be assigned
    client.patch(f"/api/v1/admin/users/{a1}/status", json={"account_status": "inactive"}, headers=admin)
    tid2 = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    assert client.patch(f"/api/v1/tickets/{tid2}/assign", json={"agent_id": a1}, headers=admin).status_code == 422
    wl = client.get("/api/v1/agents/workload", headers=admin).get_json()["data"]
    assert {w["user_id"] for w in wl} >= {a1, a2}


def test_status_transition_validation(client, admin, agent1, cust1):
    tid = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "bogus"}, headers=admin).status_code == 422
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "open"}, headers=admin).status_code == 409
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "assigned"}, headers=admin).status_code == 409  # no agent
    # customer cannot resolve or set in progress
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "resolved"}, headers=cust1).status_code == 409
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "in_progress"}, headers=cust1).status_code == 409
    # closed ticket cannot jump to resolved
    client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "closed"}, headers=admin)
    assert client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "resolved"}, headers=admin).status_code == 409
    # customer can reopen their closed ticket
    r = client.patch(f"/api/v1/tickets/{tid}/status", json={"status": "open"}, headers=cust1)
    assert r.status_code == 200 and r.get_json()["data"]["closed_at"] is None


def test_agent_cannot_set_open_or_assigned(client, agent1):
    t = client.get("/api/v1/agents/tickets", headers=agent1).get_json()["data"][0]
    assert client.patch(f"/api/v1/tickets/{t['ticket_id']}/status", json={"status": "open"}, headers=agent1).status_code == 409


def test_priority_updates_and_sla_recompute(client, admin, agent1, cust1):
    t = new_ticket(client, cust1, priority="low").get_json()["data"]
    tid = t["ticket_id"]
    assert client.patch(f"/api/v1/tickets/{tid}/priority", json={"priority": "high"}, headers=cust1).status_code == 403
    r = client.patch(f"/api/v1/tickets/{tid}/priority", json={"priority": "critical"}, headers=admin)
    assert r.status_code == 200
    assert r.get_json()["data"]["sla"]["resolution_due_at"] < t["sla"]["resolution_due_at"]
    assert client.patch(f"/api/v1/tickets/{tid}/priority", json={"priority": "nope"}, headers=admin).status_code == 422
    hist = client.get(f"/api/v1/tickets/{tid}/history", headers=admin).get_json()["data"]
    assert any(h["event_type"] == "priority" and h["new_value"] == "critical" for h in hist)


def test_customer_cannot_pick_critical_and_validation(client, cust1):
    assert new_ticket(client, cust1, priority="critical").status_code == 422
    assert new_ticket(client, cust1, subject="no").status_code == 422
    assert new_ticket(client, cust1, category_id=9999).status_code == 422
    assert client.post("/api/v1/tickets", data="notjson", headers=cust1).status_code == 400


def test_ticket_numbers_unique(client, cust1):
    nums = {new_ticket(client, cust1).get_json()["data"]["ticket_number"] for _ in range(5)}
    assert len(nums) == 5


def test_edit_ticket_rules(client, cust1, admin, agent1):
    tid = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    r = client.put(f"/api/v1/tickets/{tid}", json={"subject": "Updated subject here"}, headers=cust1)
    assert r.status_code == 200 and r.get_json()["data"]["subject"] == "Updated subject here"
    aid = _agent_id(client, agent1)
    client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": aid}, headers=admin)
    assert client.put(f"/api/v1/tickets/{tid}", json={"subject": "Changed again now"}, headers=cust1).status_code == 409


def test_search_filter_sort_pagination(client, admin, cust1):
    for i in range(12):
        new_ticket(client, cust1, subject=f"Bulk ticket number {i}", priority="low" if i % 2 else "high")
    r = client.get("/api/v1/admin/tickets?per_page=5&page=2", headers=admin).get_json()
    assert len(r["data"]) == 5 and r["pagination"]["page"] == 2 and r["pagination"]["total"] >= 16
    q = client.get("/api/v1/admin/tickets?q=Bulk ticket number 7", headers=admin).get_json()
    assert q["pagination"]["total"] == 1
    hi = client.get("/api/v1/tickets?priority=high&per_page=100", headers=cust1).get_json()["data"]
    assert hi and all(t["priority"] == "high" for t in hi)
    asc = client.get("/api/v1/admin/tickets?sort=subject&order=asc&per_page=100", headers=admin).get_json()["data"]
    subs = [t["subject"] for t in asc]
    assert subs == sorted(subs)
    st = client.get("/api/v1/admin/tickets?status=closed", headers=admin).get_json()["data"]
    assert st and all(t["status"] == "closed" for t in st)
    # LIKE wildcards are escaped
    assert client.get("/api/v1/admin/tickets?q=%25", headers=admin).get_json()["pagination"]["total"] == 0
    assert client.get("/api/v1/tickets?page=abc", headers=cust1).status_code == 400


def test_attachments_flow_and_permissions(client, admin, agent1, agent2, cust1, cust2):
    tid = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    client.patch(f"/api/v1/tickets/{tid}/assign", json={"agent_id": _agent_id(client, agent1)}, headers=admin)
    r = upload(client, cust1, tid)
    assert r.status_code == 201
    att = r.get_json()["data"][0]
    assert att["original_filename"] == "shot.png" and att["mime_type"] == "image/png"
    d = client.get(f"/api/v1/attachments/{att['attachment_id']}/download", headers=cust1)
    assert d.status_code == 200 and d.data.startswith(b"\x89PNG")
    assert client.get(f"/api/v1/attachments/{att['attachment_id']}/download", headers=agent1).status_code == 200
    assert client.get(f"/api/v1/attachments/{att['attachment_id']}/download", headers=cust2).status_code == 404
    assert client.get(f"/api/v1/attachments/{att['attachment_id']}/download", headers=agent2).status_code == 404
    assert client.get(f"/api/v1/attachments/{att['attachment_id']}/download").status_code == 401
    # internal attachment hidden from customer
    r2 = upload(client, agent1, tid, name="notes.txt", data=b"internal text", is_internal="true")
    assert r2.status_code == 201
    iid = r2.get_json()["data"][0]["attachment_id"]
    assert client.get(f"/api/v1/attachments/{iid}/download", headers=cust1).status_code == 404
    assert len(client.get(f"/api/v1/tickets/{tid}/attachments", headers=cust1).get_json()["data"]) == 1
    assert len(client.get(f"/api/v1/tickets/{tid}/attachments", headers=agent1).get_json()["data"]) == 2
    # delete rules
    assert client.delete(f"/api/v1/attachments/{att['attachment_id']}", headers=agent1).status_code == 403
    assert client.delete(f"/api/v1/attachments/{att['attachment_id']}", headers=cust1).status_code == 200


def test_attachment_validation(client, cust1):
    tid = new_ticket(client, cust1).get_json()["data"]["ticket_id"]
    assert upload(client, cust1, tid, name="evil.exe", data=b"MZ\x90\x00").status_code == 422
    assert upload(client, cust1, tid, name="fake.png", data=b"<?php echo 1; ?>").status_code == 422  # content != extension
    assert upload(client, cust1, tid, name="fake.pdf", data=b"not a pdf").status_code == 422
    assert upload(client, cust1, tid, name="bin.txt", data=b"abc\x00def").status_code == 422
    assert upload(client, cust1, tid, name="x.docx", data=b"PK-not-really").status_code == 422
    assert upload(client, cust1, tid, name="ok.pdf", data=b"%PDF-1.4 fake body").status_code == 201
    big = b"\x89PNG\r\n\x1a\n" + b"0" * (5 * 1024 * 1024 + 10)
    assert upload(client, cust1, tid, name="big.png", data=big).status_code in (413, 422)
    assert client.post(f"/api/v1/tickets/{tid}/attachments", headers=cust1).status_code == 400
    # path traversal in filename is neutralised
    r = upload(client, cust1, tid, name="../../etc/passwd.txt", data=b"hello")
    assert r.status_code == 201 and "/" not in r.get_json()["data"][0]["original_filename"]
