import asyncio
import uuid

import pytest
import httpx

from app.main import app, users, tokens


@pytest.fixture
def event_loop():
    """Отдельный цикл событий для теста (требование задания)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def clear_storage():
    users.clear()
    tokens.clear()
    yield
    users.clear()
    tokens.clear()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as async_client:
        yield async_client


@pytest.fixture
async def registered_user(client):
    suffix = uuid.uuid4().hex[:8]
    data = {
        "username": f"user_{suffix}",
        "password": "StrongPass123",
        "email": f"{suffix}@example.com",
        "name": "Test User",
    }
    response = await client.post("/api/register", json=data)
    assert response.status_code == 201
    return data


@pytest.fixture
async def auth_headers(client, registered_user):
    response = await client.post(
        "/api/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
