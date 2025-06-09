import pytest
from httpx import AsyncClient
from ..app.main import app
from ..app.database import init_db, engine, metadata
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(autouse=True)
def setup_db():
    metadata.drop_all(engine)
    metadata.create_all(engine)
    init_db()

@pytest.mark.asyncio
async def test_register_login_and_tasks():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/auth/register", json={"username": "u","password": "p"})
        assert resp.status_code == 201

        resp = await client.post("/auth/login", json={"username": "u","password": "p"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post("/tasks", headers=headers, json={"title": "Test"})
        assert resp.status_code == 200
        tid = resp.json()["id"]

        resp = await client.get("/tasks", headers=headers)
        assert resp.status_code == 200
        tasks = resp.json()
        assert tasks[0]["title"] == "Test"

        resp = await client.put(f"/tasks/{tid}", headers=headers, json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

        resp = await client.delete(f"/tasks/{tid}", headers=headers)
        assert resp.status_code == 204

        resp = await client.get("/tasks", headers=headers)
        assert resp.json() == []