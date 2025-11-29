from fastapi.testclient import TestClient
from src.app import app
import pytest

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser_pytest@example.com"

    # Ensure clean state: if email already present, remove it
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # attempt to remove to start fresh
        client.delete(f"/activities/{activity}/participants?email={email}")

    # Sign up the test user
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json()["message"]

    # Verify the participant is present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should return 400
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Unregister the participant
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json()["message"]

    # Verify removal
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Deleting again should return 404
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
