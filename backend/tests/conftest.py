# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from app.database import Base, get_db
from .database_test import override_get_db, engine as test_engine
from app import schemas, crud

@pytest.fixture(scope="function")
def db_session():
    # Create the database tables
    Base.metadata.create_all(bind=test_engine)
    db = next(override_get_db())
    yield db
    # Teardown: drop all tables after the test is done
    db.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def test_client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def reporter_auth_token(test_client, db_session: Session):
    user_in = schemas.UserCreate(email="reporter@example.com", password="password", role=schemas.UserRole.REPORTER)
    crud.create_user(db=db_session, user=user_in)
    
    response = test_client.post(
        "/api/v1/token",
        data={"username": "reporter@example.com", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def maintainer_auth_token(test_client, db_session: Session):
    user_in = schemas.UserCreate(email="maintainer@example.com", password="password", role=schemas.UserRole.MAINTAINER)
    crud.create_user(db=db_session, user=user_in)

    response = test_client.post(
        "/api/v1/token",
        data={"username": "maintainer@example.com", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def admin_auth_token(test_client, db_session: Session):
    user_in = schemas.UserCreate(email="admin@example.com", password="password", role=schemas.UserRole.ADMIN)
    crud.create_user(db=db_session, user=user_in)

    response = test_client.post(
        "/api/v1/token",
        data={"username": "admin@example.com", "password": "password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]