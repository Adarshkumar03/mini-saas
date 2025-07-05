# backend/tests/test_auth.py
from app.auth import create_access_token # Adjust import path
from datetime import timedelta

def test_create_access_token():
    data = {"sub": "test@example.com", "role": "ADMIN"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)