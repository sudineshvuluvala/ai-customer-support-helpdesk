import io

import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.seed import seed_database

PW = "Demo@12345"


@pytest.fixture()
def app(tmp_path):
    class Cfg(TestConfig):
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    app = create_app(Cfg)
    with app.app_context():
        db.create_all()
        seed_database(PW)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email, password=PW):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.get_json()
    return {"Authorization": "Bearer " + r.get_json()["data"]["token"]}


@pytest.fixture()
def admin(client):
    return login(client, "admin@helpdesk.local")


@pytest.fixture()
def agent1(client):
    return login(client, "agent1@helpdesk.local")


@pytest.fixture()
def agent2(client):
    return login(client, "agent2@helpdesk.local")


@pytest.fixture()
def cust1(client):
    return login(client, "customer1@helpdesk.local")


@pytest.fixture()
def cust2(client):
    return login(client, "customer2@helpdesk.local")


def new_ticket(client, headers, **over):
    cats = client.get("/api/v1/categories", headers=headers).get_json()["data"]
    body = {"subject": "Printer is on fire", "description": "The device is smoking since this morning.",
            "category_id": cats[0]["category_id"], "priority": "medium"}
    body.update(over)
    return client.post("/api/v1/tickets", json=body, headers=headers)


PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def upload(client, headers, ticket_id, name="shot.png", data=PNG, **form):
    return client.post(f"/api/v1/tickets/{ticket_id}/attachments", headers=headers,
                       data={"file": (io.BytesIO(data), name), **form}, content_type="multipart/form-data")
