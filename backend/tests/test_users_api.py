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
    
