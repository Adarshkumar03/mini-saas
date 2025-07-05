# backend/tests/test_users_api.py
from fastapi.testclient import TestClient

def test_read_users_permissions(
    test_client: TestClient,
    reporter_auth_token: str,
    admin_auth_token: str
):
    # 1. Attempt to get users as a REPORTER (should fail)
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    response = test_client.get("/api/v1/users/", headers=reporter_headers)
    assert response.status_code == 403  # Forbidden

    # 2. Attempt to get users as an ADMIN (should succeed)
    admin_headers = {"Authorization": f"Bearer {admin_auth_token}"}
    response = test_client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200

    # Ensure the response contains a list of users
    # We expect at least the admin user we created in the fixture
    user_list = response.json()
    assert isinstance(user_list, list)
    assert len(user_list) >= 1
    assert "admin@example.com" in [user["email"] for user in user_list]
    
def test_create_user_permissions(
    test_client: TestClient,
    admin_auth_token: str
):
    # 1. Attempt to create a user as an ADMIN (should succeed)
    admin_headers = {"Authorization": f"Bearer {admin_auth_token}"}
    new_user_data = {
        "email": "new.user@example.com",
        "password": "password123",
        "role": "REPORTER"
    }

    response = test_client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert created_user["role"] == new_user_data["role"]
    
def test_create_user_permissions_restricted(
    test_client: TestClient,
    reporter_auth_token: str
):
    # 1. Attempt to create a user as a REPORTER (should work)
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    new_user_data = {
        "email": "restricted.user@example.com",
        "password": "password123",
        "role": "REPORTER"
    }
    response = test_client.post("/api/v1/users/", json=new_user_data, headers=reporter_headers)
    assert response.status_code == 201  # Created
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert created_user["role"] == new_user_data["role"]

def test_update_user_permissions(
    test_client: TestClient,
    admin_auth_token: str,
    reporter_auth_token: str
):
    # 1. Create a user to update
    admin_headers = {"Authorization": f"Bearer {admin_auth_token}"}
    new_user_data = {
        "email": "user.to.update@example.com",
        "password": "password123",
        "role": "REPORTER"
    }
    response = test_client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
    assert response.status_code == 201  # Created
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert created_user["role"] == new_user_data["role"]

    # 2. Update the user as an ADMIN (should succeed)
    update_user_data = {
        "email": "user.to.update@example.com",
        "password": "newpassword123",
        "role": "ADMIN"
    }
    response = test_client.put(f"/api/v1/users/{created_user['id']}", json=update_user_data, headers=admin_headers)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == update_user_data["email"]
    assert updated_user["role"] == update_user_data["role"]

    # 3. Attempt to update the user as a REPORTER (should fail)
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    response = test_client.put(f"/api/v1/users/{created_user['id']}", json=update_user_data, headers=reporter_headers)
    assert response.status_code == 403  # Forbidden
    assert response.json() == {"detail": "Not enough permissions to update this user's profile"}

def test_delete_user_permissions(
    test_client: TestClient,
    admin_auth_token: str,
    reporter_auth_token: str
):
    # 1. Create a user to delete
    admin_headers = {"Authorization": f"Bearer {admin_auth_token}"}
    new_user_data = {
        "email": "user.to.delete@example.com",
        "password": "password123",
        "role": "REPORTER"
    }
    response = test_client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
    assert response.status_code == 201  # Created
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert created_user["role"] == new_user_data["role"]

    # 2. Attempt to delete the user as a REPORTER (should fail)
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    response = test_client.delete(f"/api/v1/users/{created_user['id']}", headers=reporter_headers)
    assert response.status_code == 403  # Forbidden

    # 3. Delete the user as the admin (should succeed)
    response = test_client.delete(f"/api/v1/users/{created_user['id']}", headers=admin_headers)
    assert response.status_code == 204  # No Content

    # 4. Verify the user is gone
    response = test_client.get(f"/api/v1/users/{created_user['id']}", headers=admin_headers)
    assert response.status_code == 404  # Not Found
    
def test_get_user_by_id_permissions(
    test_client: TestClient,
    admin_auth_token: str,
    reporter_auth_token: str
):
    # 1. Create a user to retrieve
    admin_headers = {"Authorization": f"Bearer {admin_auth_token}"}
    new_user_data = {
        "email": "user.to.retrieve@example.com",
        "password": "password123",
        "role": "REPORTER"
    }
    response = test_client.post("/api/v1/users/", json=new_user_data, headers=admin_headers)
    assert response.status_code == 201  # Created
    created_user = response.json()
    assert created_user["email"] == new_user_data["email"]
    assert created_user["role"] == new_user_data["role"]

    # 2. Get the user by ID as an ADMIN (should succeed)
    response = test_client.get(f"/api/v1/users/{created_user['id']}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created_user["id"]

    # 3. Get the user by ID as a REPORTER (should fail)
    reporter_headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    response = test_client.get(f"/api/v1/users/{created_user['id']}", headers=reporter_headers)
    assert response.status_code == 403  # Forbidden
    
def test_get_current_user(
    test_client: TestClient,
    reporter_auth_token: str
):
    # 1. Get the current user as a REPORTER (should succeed)
    headers = {"Authorization": f"Bearer {reporter_auth_token}"}
    response = test_client.get("/api/v1/users/me/", headers=headers)
    assert response.status_code == 200
    current_user = response.json()
    assert current_user["email"] == "reporter@example.com"
    assert current_user["role"] == "REPORTER"
    