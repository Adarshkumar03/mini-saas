# backend/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..crud import verify_password
from ..database import get_db
from ..auth import create_access_token, get_current_user, require_admin, require_maintainer_or_admin, require_reporter_or_higher # Import new RBAC dependencies

router = APIRouter(
    prefix="/api/v1",
    tags=["Users", "Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user. This endpoint is currently public for self-registration.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Retrieve information about the current authenticated user. Accessible to all authenticated roles.
    """
    return current_user

# Protected endpoint: Only ADMINs can read all users
@router.get("/users/", response_model=List[schemas.User], dependencies=[Depends(require_admin)])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # current_user is passed through require_admin, no need to declare again
):
    """
    Retrieve a list of all users with pagination. Requires ADMIN role.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# Protected endpoint: ADMIN can read any user, others can read their own
@router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Get current user first
):
    """
    Retrieve a single user by ID. ADMINs can read any user. Others can read only their own profile.
    """
    # Check if the current user is an ADMIN
    if current_user.role == models.UserRole.ADMIN:
        db_user = crud.get_user(db, user_id=user_id)
    # If not ADMIN, allow access only if requesting their own ID
    elif current_user.id == user_id:
        db_user = current_user # Already have the current user object
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to read this user's profile"
        )

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Protected endpoint: ADMIN can update any user, others can update their own (excluding role)
@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update_data: schemas.UserUpdate, # Renamed parameter to avoid conflict
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing user's information. ADMINs can update any user. Others can update their own profile (excluding role).
    """
    db_user_to_update = crud.get_user(db, user_id=user_id)
    if db_user_to_update is None:
        raise HTTPException(status_code=404, detail="User not found")

    # If not ADMIN, restrict to updating self only
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user's profile"
        )

    # If user is not ADMIN, prevent them from changing their own role
    if current_user.role != models.UserRole.ADMIN and user_update_data.role is not None:
        if user_update_data.role != current_user.role: # Allow if they are trying to set their role to their current role
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to change user role"
            )

    db_user = crud.update_user(db, user_id=user_id, user_update=user_update_data) # Pass the renamed parameter
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Protected endpoint: Only ADMINs can delete users
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user is passed through require_admin, no need to declare again
):
    """
    Delete a user by ID. Requires ADMIN role.
    """
    result = crud.delete_user(db, user_id=user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return
