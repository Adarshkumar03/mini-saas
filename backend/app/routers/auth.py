# backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from .. import crud, schemas
from ..database import get_db
from ..auth import create_access_token
from ..crud import verify_password

logger = logging.getLogger(__name__)

# Create an APIRouter instance for authentication endpoints
router = APIRouter(
    prefix="/v1", # FIX: Changed prefix from "/api/v1" to "/v1"
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    Takes username (email) and password from form data.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Failed login attempt", extra={"email": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    logger.info("User logged in successfully", extra={"user_email": user.email, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

