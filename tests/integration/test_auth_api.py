"""Integration tests for Authentication API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    payload = {
        "email": "newdev@devlens.internal",
        "password": "SecurePassword123!",
        "full_name": "New Developer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_weak_password_rejected(client: TestClient):
    payload = {
        "email": "weak@devlens.internal",
        "password": "weak",
        "full_name": "Weak User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_duplicate_email_rejected(client: TestClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client: TestClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "DevLens@Secure2026!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(client: TestClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_refresh_token_rotation(client: TestClient, test_user):
    # First login to obtain refresh token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "DevLens@Secure2026!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Use refresh token to obtain a new one
    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert data["refresh_token"] != refresh_token  # Must have rotated

    # Attempting to reuse old refresh token must be rejected
    reuse_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert reuse_resp.status_code == 401


def test_get_current_user_profile(client: TestClient, auth_headers, test_user):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


def test_delete_user_account_cascades(client: TestClient, auth_headers):
    response = client.delete("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert "permanently purged" in response.json()["message"]

    # Subsequent access with same token must fail
    me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 401
