# backend/app/main_test.py
from fastapi.testclient import TestClient
from main import app
from app.database import Base, engine, get_db
from .database_test import override_get_db, engine as test_engine

# Override the get_db dependency for all tests
app.dependency_overrides[get_db] = override_get_db

# Create and drop the test database tables for each test run
Base.metadata.create_all(bind=test_engine)
# You might need a teardown strategy for more complex tests

# Create a TestClient
client = TestClient(app)