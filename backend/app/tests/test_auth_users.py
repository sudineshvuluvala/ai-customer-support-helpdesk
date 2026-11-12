from .conftest import PW, login


def test_register_login_me_logout(client):
    r = client.post("/api/v1/auth/register", json={"name": "New Person", "email": "New@Example.com", "password": "Passw0rdX"})
    assert r.status_code == 201
    assert r.get_json()["data"]["role"] == "customer"
    h = login(client, "new@example.com", "Passw0rdX")
    me = client.get("/api/v1/auth/me", headers=h)
    assert me.status_code == 200 and me.get_json()["data"]["email"] == "new@example.com"
    assert "password_hash" not in me.get_json()["data"]
    assert client.post("/api/v1/auth/logout", headers=h).status_code == 200
    assert client.get("/api/v1/auth/me", headers=h).status_code == 401  # token revoked


def test_register_cannot_choose_role(client):
    r = client.post("/api/v1/auth/register", json={"name": "Sneaky", "email": "s@example.com", "password": "Passw0rdX", "role": "admin"})
    assert r.get_json()["data"]["role"] == "customer"


def test_duplicate_email_and_validation(client):
    body = {"name": "Dup", "email": "customer1@helpdesk.local", "password": "Passw0rdX"}
    assert client.post("/api/v1/auth/register", json=body).status_code == 409
    r = client.post("/api/v1/auth/register", json={"name": "A", "email": "bad", "password": "short"})
    assert r.status_code == 422 and set(r.get_json()["error"]["details"]) == {"name", "email", "password"}


def test_login_failures(client):
    assert client.post("/api/v1/auth/login", json={"email": "admin@helpdesk.local", "password": "wrong"}).status_code == 401
    assert client.post("/api/v1/auth/login", json={"email": "nobody@x.com", "password": PW}).status_code == 401


def test_protected_routes_require_token(client):
    assert client.get("/api/v1/tickets").status_code == 401
    assert client.get("/api/v1/tickets", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_password_hashed(app):
    from app.models import User
    u = User.query.filter_by(email="admin@helpdesk.local").first()
    assert u.password_hash != "Demo@12345" and u.password_hash.startswith(("scrypt:", "pbkdf2:"))


def test_deactivated_account_blocked(client, admin, cust1):
    uid = client.get("/api/v1/auth/me", headers=cust1).get_json()["data"]["user_id"]
    r = client.patch(f"/api/v1/admin/users/{uid}/status", json={"account_status": "inactive"}, headers=admin)
    assert r.status_code == 200
    assert client.get("/api/v1/auth/me", headers=cust1).status_code == 403  # existing token rejected
    assert client.post("/api/v1/auth/login", json={"email": "customer1@helpdesk.local", "password": PW}).status_code == 403


def test_role_authorization(client, admin, agent1, cust1):
    for path in ("/api/v1/admin/dashboard", "/api/v1/admin/users", "/api/v1/admin/audit-logs", "/api/v1/users", "/api/v1/admin/tickets"):
        assert client.get(path, headers=admin).status_code == 200, path
        assert client.get(path, headers=agent1).status_code == 403, path
        assert client.get(path, headers=cust1).status_code == 403, path
    assert client.post("/api/v1/admin/agents", json={}, headers=agent1).status_code == 403
    assert client.get("/api/v1/agents/dashboard", headers=cust1).status_code == 403
    assert client.get("/api/v1/agents/dashboard", headers=admin).status_code == 403
    assert client.post("/api/v1/categories", json={"category_name": "X"}, headers=agent1).status_code == 403
    assert client.post("/api/v1/knowledge/articles", json={}, headers=cust1).status_code == 403


def test_admin_user_and_agent_management(client, admin):
    r = client.post("/api/v1/admin/agents", json={"name": "Agent Eve", "email": "eve@helpdesk.local", "password": "Passw0rdX"}, headers=admin)
    assert r.status_code == 201 and r.get_json()["data"]["role"] == "agent"
    uid = r.get_json()["data"]["user_id"]
    assert client.put(f"/api/v1/admin/users/{uid}", json={"name": "Agent Eve Renamed"}, headers=admin).get_json()["data"]["name"] == "Agent Eve Renamed"
    agents = client.get("/api/v1/admin/agents", headers=admin).get_json()
    assert any(a["user_id"] == uid for a in agents["data"])
    custs = client.get("/api/v1/admin/users?role=customer&q=carol", headers=admin).get_json()
    assert custs["pagination"]["total"] == 1
    me = client.get("/api/v1/auth/me", headers=admin).get_json()["data"]
    assert client.patch(f"/api/v1/admin/users/{me['user_id']}/status", json={"account_status": "inactive"}, headers=admin).status_code == 409


def test_profile_update(client, cust1):
    r = client.put("/api/v1/users/profile", json={"name": "Carol Changed"}, headers=cust1)
    assert r.get_json()["data"]["name"] == "Carol Changed"
    bad = client.put("/api/v1/users/profile", json={"current_password": "nope", "new_password": "Newpass123"}, headers=cust1)
    assert bad.status_code == 422
    ok = client.put("/api/v1/users/profile", json={"current_password": PW, "new_password": "Newpass123"}, headers=cust1)
    assert ok.status_code == 200
    assert client.post("/api/v1/auth/login", json={"email": "customer1@helpdesk.local", "password": "Newpass123"}).status_code == 200
