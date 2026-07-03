"""Integration tests for chat endpoints."""

import pytest
from fastapi import status

BASE_AUTH = "/api/v1/auth"
BASE_CHAT = "/api/v1/chats"


async def _register_and_login(client, username: str, email: str) -> str:
    """Helper: register + login, return access token."""
    await client.post(f"{BASE_AUTH}/register", json={
        "username": username,
        "email": email,
        "password": "SecurePass1!",
    })
    resp = await client.post(f"{BASE_AUTH}/login", json={
        "email": email,
        "password": "SecurePass1!",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_direct_chat(client):
    token_a = await _register_and_login(client, "chata", "chata@example.com")
    token_b = await _register_and_login(client, "chatb", "chatb@example.com")

    # Get user B's ID
    me_b = await client.get(f"{BASE_AUTH}/me", headers={"Authorization": f"Bearer {token_b}"})
    user_b_id = me_b.json()["id"]

    # User A opens a chat with B
    resp = await client.post(
        f"{BASE_CHAT}/direct",
        json={"target_user_id": user_b_id},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["is_group"] is False


@pytest.mark.asyncio
async def test_create_group_chat(client):
    token = await _register_and_login(client, "groupowner", "groupowner@example.com")
    token2 = await _register_and_login(client, "groupmember", "groupmember@example.com")

    me2 = await client.get(f"{BASE_AUTH}/me", headers={"Authorization": f"Bearer {token2}"})
    uid2 = me2.json()["id"]

    resp = await client.post(
        f"{BASE_CHAT}/group",
        json={"name": "Test Group", "description": "A test group", "member_ids": [uid2]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["is_group"] is True


@pytest.mark.asyncio
async def test_list_chats(client):
    token = await _register_and_login(client, "listchats", "listchats@example.com")
    resp = await client.get(BASE_CHAT, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)
