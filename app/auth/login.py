from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, database, schemas
from app.auth.dependencies import oauth2_scheme, get_current_user
from app.auth.utils import verify_password, create_access_token, remove_old_token
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=TokenResponse, summary="Login user")
def login(login_data: LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    remove_old_token(db, user.id)
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return TokenResponse(access_token=access_token, token_type="bearer")

from app.auth.utils import add_to_blacklist

@router.post("/logout", summary="Logout user")
def logout(token: str = Depends(oauth2_scheme),
           db: Session = Depends(database.get_db),
           current_user: schemas.User = Depends(get_current_user)):
    add_to_blacklist(db, token, user_id = current_user.id)
    return {"message": "Successfully logged out"}