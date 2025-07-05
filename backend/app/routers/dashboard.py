# backend/app/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..auth import require_maintainer_or_admin

# Create an APIRouter instance for dashboard endpoints
router = APIRouter(
    prefix="/api/v1/dashboard", # All routes in this router will be prefixed with /api/v1/dashboard
    tags=["Dashboard"], # Tag for organizing in OpenAPI documentation
)

@router.get("/status_counts", response_model=schemas.DashboardData)
async def get_dashboard_status_counts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_maintainer_or_admin) # Only Maintainers and Admins can view dashboard
):
    """
    Retrieve aggregated issue counts by status for the dashboard.
    Requires MAINTAINER or ADMIN role.
    """
    status_counts = crud.get_issue_status_counts(db)
    return schemas.DashboardData(status_counts=status_counts)

