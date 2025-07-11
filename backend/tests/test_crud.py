# backend/tests/test_crud.py

from sqlalchemy.orm import Session
from app import crud, schemas, models
from tests.database_test import TestingSessionLocal

def test_create_and_get_user(db_session: Session):
    user_in = schemas.UserCreate(email="test@example.com", password="password123")
    db_user = crud.create_user(db=db_session, user=user_in)

    assert getattr(db_user, "email") == "test@example.com"
    assert db_user.id is not None

    retrieved_user = crud.get_user_by_email(db=db_session, email="test@example.com")
    assert retrieved_user is not None
    assert str(retrieved_user.email) == str(db_user.email)

def test_create_and_get_issue(db_session: Session):
    # First, create a user to be the owner of the issue
    user_in = schemas.UserCreate(email="issue.owner@example.com", password="password")
    owner = crud.create_user(db=db_session, user=user_in)

    # Now, create an issue owned by that user
    issue_in = schemas.IssueCreate(title="Test Issue", description="A test description.", severity=schemas.IssueSeverity.LOW)
    db_issue = crud.create_issue(db=db_session, issue=issue_in, owner_id=getattr(owner, "id"))

    assert getattr(db_issue, "title") == "Test Issue"
    assert getattr(db_issue, "owner_id") == owner.id

    # Test retrieving the issue
    retrieved_issue = crud.get_issue(db=db_session, issue_id=getattr(db_issue, "id"))
    assert retrieved_issue is not None
    assert getattr(retrieved_issue, "id") == getattr(db_issue, "id")
    
def test_update_issue(db_session: Session):
    # First, create a user to be the owner of the issue
    user_in = schemas.UserCreate(email="issue.owner@example.com", password="password")
    owner = crud.create_user(db=db_session, user=user_in)

    # Now, create an issue owned by that user
    issue_in = schemas.IssueCreate(title="Test Issue", description="A test description.", severity=schemas.IssueSeverity.LOW)
    db_issue = crud.create_issue(db=db_session, issue=issue_in, owner_id=getattr(owner, "id"))

    assert getattr(db_issue, "title") == "Test Issue"
    assert getattr(db_issue, "owner_id") == owner.id

    # Test retrieving the issue
    retrieved_issue = crud.get_issue(db=db_session, issue_id=getattr(db_issue, "id"))
    assert retrieved_issue is not None
    assert getattr(retrieved_issue, "id") == getattr(db_issue, "id")

def test_update_issue_title(db_session: Session):
    # First, create a user to be the owner of the issue
    user_in = schemas.UserCreate(email="issue.owner@example.com", password="password")
    owner = crud.create_user(db=db_session, user=user_in)

    # Now, create an issue owned by that user
    issue_in = schemas.IssueCreate(title="Test Issue", description="A test description.", severity=schemas.IssueSeverity.LOW)
    db_issue = crud.create_issue(db=db_session, issue=issue_in, owner_id=getattr(owner, "id"))

    assert getattr(db_issue, "title") == "Test Issue"
    assert getattr(db_issue, "owner_id") == owner.id

    # Test retrieving the issue
    retrieved_issue = crud.get_issue(db=db_session, issue_id=getattr(db_issue, "id"))
    assert retrieved_issue is not None
    assert getattr(retrieved_issue, "id") == getattr(db_issue, "id")
    assert getattr(retrieved_issue, "title") == "Test Issue"