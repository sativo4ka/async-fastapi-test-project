import allure
import pytest


@allure.feature("Регистрация")
@pytest.mark.asyncio
async def test_register_success(client, event_loop):
    payload = {
        "username": "new_user",
        "password": "StrongPass123",
        "email": "new_user@example.com",
        "name": "New User",
    }
    response = await client.post("/api/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


@allure.feature("Регистрация")
@pytest.mark.asyncio
async def test_register_duplicate_username(client, registered_user, event_loop):
    payload = {
        **registered_user,
        "email": "another@example.com",
    }
    response = await client.post("/api/register", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


@allure.feature("Регистрация")
@pytest.mark.asyncio
async def test_register_invalid_email(client, event_loop):
    response = await client.post("/api/register", json={
        "username": "bad_email",
        "password": "StrongPass123",
        "email": "not-an-email",
        "name": "Bad Email",
    })

    assert response.status_code == 422


@allure.feature("Регистрация")
@pytest.mark.asyncio
async def test_register_short_password(client, event_loop):
    response = await client.post("/api/register", json={
        "username": "short_pass",
        "password": "123",
        "email": "short@example.com",
        "name": "Short Password",
    })

    assert response.status_code == 422


@allure.feature("Авторизация")
@pytest.mark.asyncio
async def test_login_success(client, registered_user, event_loop):
    response = await client.post("/api/login", json={
        "username": registered_user["username"],
        "password": registered_user["password"],
    })

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


@allure.feature("Авторизация")
@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user, event_loop):
    response = await client.post("/api/login", json={
        "username": registered_user["username"],
        "password": "WrongPassword",
    })

    assert response.status_code == 401


@allure.feature("Авторизация")
@pytest.mark.asyncio
async def test_login_unknown_user(client, event_loop):
    response = await client.post("/api/login", json={
        "username": "unknown_user",
        "password": "StrongPass123",
    })

    assert response.status_code == 401


@allure.feature("Профиль")
@pytest.mark.asyncio
async def test_get_profile_success(client, registered_user, auth_headers, event_loop):
    response = await client.get("/api/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "username": registered_user["username"],
        "email": registered_user["email"],
        "name": registered_user["name"],
    }


@allure.feature("Профиль")
@pytest.mark.asyncio
async def test_get_profile_without_token(client, event_loop):
    response = await client.get("/api/profile")

    assert response.status_code == 401


@allure.feature("Профиль")
@pytest.mark.asyncio
async def test_get_profile_invalid_token(client, event_loop):
    response = await client.get(
        "/api/profile",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


@allure.feature("Редактирование профиля")
@pytest.mark.asyncio
async def test_update_profile_success(client, registered_user, auth_headers, event_loop):
    response = await client.put(
        "/api/profile",
        headers=auth_headers,
        json={"email": "updated@example.com", "name": "Updated User"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": registered_user["username"],
        "email": "updated@example.com",
        "name": "Updated User",
    }


@allure.feature("Редактирование профиля")
@pytest.mark.asyncio
async def test_update_profile_without_token(client, event_loop):
    response = await client.put(
        "/api/profile",
        json={"name": "Hacker"},
    )

    assert response.status_code == 401


@allure.feature("Редактирование профиля")
@pytest.mark.asyncio
async def test_update_profile_invalid_email(client, auth_headers, event_loop):
    response = await client.put(
        "/api/profile",
        headers=auth_headers,
        json={"email": "wrong-email"},
    )

    assert response.status_code == 422
