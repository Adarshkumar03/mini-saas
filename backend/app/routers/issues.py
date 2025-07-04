# backend/app/routers/issues.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas
from ..database import get_db
from ..auth import get_current_user, require_admin, require_maintainer_or_admin, require_reporter_or_higher

# Create an APIRouter instance for issue-related endpoints
router = APIRouter(
    prefix="/api/v1/issues", # All routes in this router will be prefixed with /api/v1/issues
    tags=["Issues"], # Tags for organizing in OpenAPI documentation
    responses={404: {"description": "Issue not found"}},
)

@router.post("/", response_model=schemas.Issue, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Only authenticated users can create issues
):
    """
    Create a new issue. Reporters can create their own issues.
    """
    # Reporters can only create issues for themselves (their owner_id will be current_user.id)
    # Maintainers and Admins can also create issues
    return crud.create_issue(db=db, issue=issue, owner_id=current_user.id)


@router.get("/", response_model=List[schemas.Issue])
async def read_issues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # All authenticated users can view issues
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
    current_user: models.User = Depends(get_current_user) # All authenticated users can view issues
):
    """
    Retrieve a single issue by ID.
    - ADMINs and MAINTAINERs can view any issue.
    - REPORTERs can view only issues they created.
    """
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check permissions
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
    current_user: models.User = Depends(get_current_user) # Only authenticated users can update issues
):
    """
    Update an existing issue.
    - ADMINs and MAINTAINERs can update any issue.
    - REPORTERs can only update the title and description of their own OPEN issues.
    """
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # ADMINs and MAINTAINERs have full update permissions
    if current_user.role == models.UserRole.ADMIN or current_user.role == models.UserRole.MAINTAINER:
        pass # No additional checks needed here, they can update anything
    # REPORTERs have limited update permissions on their own issues
    elif current_user.role == models.UserRole.REPORTER:
        if db_issue.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this issue"
            )
        # Reporters can only update title and description, and only if the issue is OPEN
        if db_issue.status != models.IssueStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reporters can only update OPEN issues."
            )
        # Ensure reporters are not trying to change status or severity
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
        # Filter update data for reporters
        allowed_updates = {}
        if issue_update_data.title is not None:
            allowed_updates['title'] = issue_update_data.title
        if issue_update_data.description is not None:
            allowed_updates['description'] = issue_update_data.description
        issue_update_data = schemas.IssueUpdate(**allowed_updates) # Create a new schema with only allowed fields
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update issues"
        )

    updated_issue = crud.update_issue(db, issue_id=issue_id, issue_update=issue_update_data)
    if updated_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found after update attempt") # Should not happen if db_issue was found
    return updated_issue

@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Only authenticated users can delete issues
):
    """
    Delete an issue by ID.
    - ADMINs can delete any issue.
    - MAINTAINERs and REPORTERs cannot delete issues.
    """
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Only ADMINs can delete issues
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete issues"
        )

    result = crud.delete_issue(db, issue_id=issue_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Issue not found after delete attempt") # Should not happen
    return
