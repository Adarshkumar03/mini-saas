# backend/app/routers/issues.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from .. import crud, models, schemas
from ..database import get_db
from ..auth import get_current_user, require_admin, require_maintainer_or_admin, require_reporter_or_higher
from ..websockets import manager # Import the WebSocket manager from the new websockets module

# Create an APIRouter instance for issue-related endpoints
router = APIRouter(
    prefix="/api/v1/issues",
    tags=["Issues"],
    responses={404: {"description": "Issue not found"}},
)

@router.post("/", response_model=schemas.Issue, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new issue. Reporters can create their own issues.
    Broadcasts a message on creation.
    """
    db_issue = crud.create_issue(db=db, issue=issue, owner_id=current_user.id)

    # Convert SQLAlchemy model to a dictionary that matches the Pydantic schema
    # This explicitly extracts the attributes needed by schemas.Issue
    issue_data_for_websocket = {
        "id": db_issue.id,
        "title": db_issue.title,
        "description": db_issue.description,
        "severity": db_issue.severity.value, # Send enum value as string
        "status": db_issue.status.value,     # Send enum value as string
        "created_at": db_issue.created_at.isoformat(), # Convert datetime to ISO format string
        "updated_at": db_issue.updated_at.isoformat(), # Convert datetime to ISO format string
        "owner_id": db_issue.owner_id
    }
    
    # Now, validate this dictionary with the Pydantic schema and dump to JSON
    message = {
        "type": "issue_created",
        "issue": schemas.Issue(**issue_data_for_websocket).model_dump_json()
    }
    await manager.broadcast(json.dumps(message))

    return db_issue


@router.get("/", response_model=List[schemas.Issue])
async def read_issues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve a list of issues.
    - ADMINs and MAINTAINERs can view all issues.
    - REPORTERs can view only issues they created.
    """
    if current_user.role == models.UserRole.ADMIN or current_user.role == models.UserRole.MAINTAINER:
        issues = crud.get_issues(db, skip=skip, limit=limit)
    elif current_user.role == models.UserRole.REPORTER:
        issues = crud.get_issues_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view issues"
        )
    return issues

@router.get("/{issue_id}", response_model=schemas.Issue)
async def read_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve a single issue by ID.
    - ADMINs and MAINTAINERs can view any issue.
    - REPORTERs can view only issues they created.
    """
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    if current_user.role == models.UserRole.ADMIN or current_user.role == models.UserRole.MAINTAINER:
        return db_issue
    elif current_user.role == models.UserRole.REPORTER and db_issue.owner_id == current_user.id:
        return db_issue
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this issue"
        )

@router.put("/{issue_id}", response_model=schemas.Issue)
async def update_issue(
    issue_id: int,
    issue_update_data: schemas.IssueUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing issue.
    - ADMINs and MAINTAINERs can update any issue.
    - REPORTERs can only update the title and description of their own OPEN issues.
    Broadcasts a message if status changes.
    """
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    original_status = db_issue.status

    if current_user.role == models.UserRole.ADMIN or current_user.role == models.UserRole.MAINTAINER:
        pass
    elif current_user.role == models.UserRole.REPORTER:
        if db_issue.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this issue"
            )
        if db_issue.status != models.IssueStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reporters can only update OPEN issues."
            )
        if issue_update_data.status is not None and issue_update_data.status != db_issue.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reporters cannot change issue status."
            )
        if issue_update_data.severity is not None and issue_update_data.severity != db_issue.severity:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reporters cannot change issue severity."
            )
        allowed_updates = {}
        if issue_update_data.title is not None:
            allowed_updates['title'] = issue_update_data.title
        if issue_update_data.description is not None:
            allowed_updates['description'] = issue_update_data.description
        issue_update_data = schemas.IssueUpdate(**allowed_updates)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update issues"
        )

    updated_issue = crud.update_issue(db, issue_id=issue_id, issue_update=issue_update_data)
    if updated_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found after update attempt")

    if original_status != updated_issue.status:
        # Convert SQLAlchemy model to a dictionary for WebSocket broadcast
        issue_data_for_websocket = {
            "id": updated_issue.id,
            "title": updated_issue.title,
            "description": updated_issue.description,
            "severity": updated_issue.severity.value,
            "status": updated_issue.status.value,
            "created_at": updated_issue.created_at.isoformat(),
            "updated_at": updated_issue.updated_at.isoformat(),
            "owner_id": updated_issue.owner_id
        }
        message = {
            "type": "issue_status_changed",
            "issue_id": updated_issue.id,
            "new_status": updated_issue.status.value, # Send enum value as string
            "issue": schemas.Issue(**issue_data_for_websocket).model_dump_json()
        }
        await manager.broadcast(json.dumps(message))

    return updated_issue

@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete an issue by ID.
    - ADMINs can delete any issue.
    - MAINTAINERs and REPORTERs cannot delete issues.
    """
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete issues"
        )

    result = crud.delete_issue(db, issue_id=issue_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Issue not found after delete attempt")

    message = {
        "type": "issue_deleted",
        "issue_id": issue_id
    }
    await manager.broadcast(json.dumps(message))

    return
