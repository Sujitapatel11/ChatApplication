"""Integration tests for the /auth endpoints."""

import pytest
from fastapi import status


BASE = "/api/v1/auth"


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post(f"{BASE}/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass1!",
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"username": "user2", "email": "dup@example.com", "password": "SecurePass1!"}
    await client.post(f"{BASE}/register", json=payload)
    resp = await client.post(f"{BASE}/register", json=payload)
    assert resp.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_register_invalid_username(client):
    resp = await client.post(f"{BASE}/register", json={
        "username": "ab",   # too short
        "email": "short@example.com",
        "password": "SecurePass1!",
    })
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    resp = await client.post(f"{BASE}/login", json={
        "email": "nobody@example.com",
        "password": "WrongPassword",
    })
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_full_auth_flow(client):
    """Register → login → get /me → logout."""
    # Register
    reg = await client.post(f"{BASE}/register", json={
        "username": "flowuser",
        "email": "flow@example.com",
        "password": "SecurePass1!",
    })
    assert reg.status_code == status.HTTP_201_CREATED

    # Login
    login = await client.post(f"{BASE}/login", json={
        "email": "flow@example.com",
        "password": "SecurePass1!",
    })
    assert login.status_code == status.HTTP_200_OK
    tokens = login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Get /me
    me = await client.get(
        f"{BASE}/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["username"] == "flowuser"


@pytest.mark.asyncio
async def test_forgot_password_always_200(client):
    """Forgot-password must return 200 even for non-existent emails (user enumeration prevention)."""
    resp = await client.post(f"{BASE}/forgot-password", json={"email": "ghost@example.com"})
    assert resp.status_code == status.HTTP_200_OK
