"""Integration tests for Analyses API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.models.user import User


def test_guest_analysis_submission(client: TestClient):
    payload = {
        "title": "Guest Python Check",
        "language": "python",
        "code": "def add(a, b):\n    return a + b\n",
        "save_history": False,
    }
    response = client.post("/api/v1/analyses", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "python"
    assert data["quality_score"] > 80.0
    assert data["is_saved"] is False
    assert "findings" in data
    assert "metrics" in data
    assert "disclaimer" in data


def test_authenticated_analysis_and_retrieval(client: TestClient, auth_headers):
    payload = {
        "title": "Secure Authenticated Scan",
        "language": "javascript",
        "code": "function greet(name) {\n    return 'Hello ' + name;\n}\n",
        "save_history": True,
    }
    create_resp = client.post("/api/v1/analyses", json=payload, headers=auth_headers)
    assert create_resp.status_code == 200
    created = create_resp.json()
    analysis_id = created["id"]
    assert created["is_saved"] is True

    # Retrieve by ID
    get_resp = client.get(f"/api/v1/analyses/{analysis_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["id"] == analysis_id
    assert retrieved["title"] == "Secure Authenticated Scan"

    # List analyses
    list_resp = client.get("/api/v1/analyses", headers=auth_headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1
    assert any(item["id"] == analysis_id for item in items)


def test_idor_protection(client: TestClient, auth_headers, db_session):
    # Create analysis for user 1
    create_resp = client.post(
        "/api/v1/analyses",
        json={"language": "python", "code": "x = 1\n", "save_history": True},
        headers=auth_headers,
    )
    analysis_id = create_resp.json()["id"]

    # User 2 attempts to access user 1's analysis
    user2 = User(
        id="user-2-uuid",
        email="attacker@devlens.internal",
        hashed_password="hashed_pwd",
        full_name="Attacker",
    )
    db_session.add(user2)
    db_session.commit()

    from backend.app.auth.security import create_access_token
    user2_token = create_access_token(subject=user2.id, extra_claims={"email": user2.email})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    idor_resp = client.get(f"/api/v1/analyses/{analysis_id}", headers=user2_headers)
    # Must return 404 Not Found to prevent resource enumeration
    assert idor_resp.status_code == 404


def test_analysis_deletion(client: TestClient, auth_headers):
    create_resp = client.post(
        "/api/v1/analyses",
        json={"language": "c", "code": "int main() { return 0; }\n", "save_history": True},
        headers=auth_headers,
    )
    analysis_id = create_resp.json()["id"]

    # Delete analysis
    del_resp = client.delete(f"/api/v1/analyses/{analysis_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    # Subsequent retrieval must return 404
    get_resp = client.get(f"/api/v1/analyses/{analysis_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_export_analysis_markdown_and_json(client: TestClient, auth_headers):
    create_resp = client.post(
        "/api/v1/analyses",
        json={"language": "python", "code": "def foo(): pass\n", "save_history": True},
        headers=auth_headers,
    )
    analysis_id = create_resp.json()["id"]

    # Export Markdown
    md_resp = client.get(f"/api/v1/analyses/{analysis_id}/export?format=markdown", headers=auth_headers)
    assert md_resp.status_code == 200
    assert "text/markdown" in md_resp.headers["content-type"]
    assert "# DevLens Code Intelligence Report" in md_resp.text

    # Export JSON
    json_resp = client.get(f"/api/v1/analyses/{analysis_id}/export?format=json", headers=auth_headers)
    assert json_resp.status_code == 200
    assert json_resp.json()["id"] == analysis_id
