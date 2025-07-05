# backend/tests/test_dashboard_api.py
from fastapi.testclient import TestClient

def test_get_dashboard_status_counts(
    test_client: TestClient,
    maintainer_auth_token: str
):
    # 1. Make an authenticated request to the dashboard endpoint
    headers = {"Authorization": f"Bearer {maintainer_auth_token}"}
    response = test_client.get("/api/v1/dashboard/status_counts", headers=headers)

    # 2. Assert that the request was successful
    assert response.status_code == 200

    # 3. Assert that the response data has the expected structure
    data = response.json()
    assert isinstance(data, dict)
    
    # --- THIS IS THE FIX ---
    # Check that the 'status_counts' key exists first
    assert "status_counts" in data
    # Now, check for the status keys inside the nested dictionary
    status_counts = data["status_counts"]
    assert "OPEN" in status_counts
    assert "IN_PROGRESS" in status_counts
    assert "DONE" in status_counts
    # --- END FIX ---