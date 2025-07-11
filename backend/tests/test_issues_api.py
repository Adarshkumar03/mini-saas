# backend/tests/test_issues_api.py

from fastapi.testclient import TestClient
from main import app
from tests.main_test import client, override_get_db # Use the test client and DB override
from app import schemas, crud
from sqlalchemy.orm import Session
import pytest

# Fixture to create a test user and token
@pytest.fixture(scope="function")
def auth_token():
    db: Session = next(override_get_db())
    # Create a test user
    user_in = schemas.UserCreate(email="reporter@example.com", password="password")
    crud.create_user(db, user_in)
    db.close()
    
    # Log in to get a token
    response = client.post(
        "/api/v1/token",
        data={"username": "reporter@example.com", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# Your existing unauthenticated test
def test_create_issue_unauthenticated(test_client: TestClient):
    response = test_client.post("/api/v1/issues/", json={"title": "Test", "severity": "MEDIUM"})
    assert response.status_code == 401

# New test for the authenticated route
def test_create_and_read_issue_authenticated(test_client: TestClient, reporter_auth_token: str):
    headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    
    issue_data = {"title": "Authenticated Test Issue", "description": "This is a test.", "severity": "HIGH"}
    response = test_client.post("/api/v1/issues/", json=issue_data, headers=headers)
    assert response.status_code == 201
    
    response = test_client.get("/api/v1/issues/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    
@pytest.fixture(scope="function")
def maintainer_auth_token():
    db: Session = next(override_get_db())
    # Create a maintainer user
    user_in = schemas.UserCreate(email="maintainer@example.com", password="password", role=schemas.UserRole.MAINTAINER)
    crud.create_user(db, user_in)
    db.close()
    
    # Log in to get a token
    response = client.post(
        "/api/v1/token",
        data={"username": "maintainer@example.com", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_update_issue_status(test_client: TestClient, reporter_auth_token: str, maintainer_auth_token: str):
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    
    issue_data = {"title": "Status Update Test", "severity": "MEDIUM"}
    response = test_client.post("/api/v1/issues/", json=issue_data, headers=reporter_headers)
    assert response.status_code == 201
    issue_id = response.json()["id"]

    status_update = {"status": "TRIAGED"}
    response = test_client.put(f"/api/v1/issues/{issue_id}", json=status_update, headers=reporter_headers)
    assert response.status_code == 403

    maintainer_headers = {"Authorization": f"Bearer {maintainer_auth_token}"}
    response = test_client.put(f"/api/v1/issues/{issue_id}", json=status_update, headers=maintainer_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "TRIAGED"
    
def test_delete_issue(test_client: TestClient, reporter_auth_token: str, admin_auth_token: str):
    # 1. Create an issue as the reporter
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    issue_data = {"title": "To Be Deleted", "severity": "LOW"}
    response = test_client.post("/api/v1/issues/", json=issue_data, headers=reporter_headers)
    assert response.status_code == 201
    issue_id = response.json()["id"]

    # 2. Try to delete the issue as the reporter (should fail)
    response = test_client.delete(f"/api/v1/issues/{issue_id}", headers=reporter_headers)
    assert response.status_code == 403 # Forbidden

    # 3. Delete the issue as the admin (should succeed)
    admin_headers = {"Authorization": f"Bearer {admin_auth_token}"}
    response = test_client.delete(f"/api/v1/issues/{issue_id}", headers=admin_headers)
    assert response.status_code == 204 # No Content

    # 4. Verify the issue is gone
    response = test_client.get(f"/api/v1/issues/{issue_id}", headers=admin_headers)
    assert response.status_code == 404 # Not Found
    
def test_get_issue_by_id(test_client: TestClient, reporter_auth_token: str):
    # Create an issue as the reporter
    headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    issue_data = {"title": "Get By ID Test", "severity": "LOW"}
    response = test_client.post("/api/v1/issues/", json=issue_data, headers=headers)
    assert response.status_code == 201
    issue_id = response.json()["id"]

    # Get the issue by ID
    response = test_client.get(f"/api/v1/issues/{issue_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == issue_id
    
def test_get_issue_by_id_not_found(test_client: TestClient, reporter_auth_token: str):
    headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    # Attempt to get an issue that does not exist
    response = test_client.get("/api/v1/issues/999999", headers=headers)
    assert response.status_code == 404
    