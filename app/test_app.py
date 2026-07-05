import os
import tempfile
import pytest

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_and_list_task(client):
    resp = client.post("/tasks", json={"title": "Write DevOps blog post"})
    assert resp.status_code == 201
    task = resp.get_json()
    assert task["title"] == "Write DevOps blog post"

    resp = client.get("/tasks")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.get_json()]
    assert "Write DevOps blog post" in titles


def test_create_task_missing_title(client):
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400


def test_delete_task(client):
    resp = client.post("/tasks", json={"title": "Temp task"})
    task_id = resp.get_json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204
