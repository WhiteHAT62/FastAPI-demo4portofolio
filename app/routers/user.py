from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud, database, models
from app.auth.dependencies import get_current_admin, get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return crud.create_user(db=db, user=user)

@router.get("/user_data", response_model=list[schemas.UserResponse])
def read_users(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource"
        )
    return crud.get_users(db=db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(
        user_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this user"
        )

    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_user(db=db, user_id=user_id)

@router.put("/{user_id}/update", response_model=schemas.UserResponse)
def update_user(
        user_id: int,
        user_update: schemas.UserUpdate,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this user"
        )
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user_update=user_update)

@router.put("/{user_id}/change_password")
def update_user_password(
        user_id: int,
        password_update: schemas.PasswordUpdate,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this user"
        )
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user_password(db=db, user_id=user_id, password_update=password_update)

@router.delete("/{user_id}/delete")
def delete_user(
        user_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this user"
        )

    if current_user.id == user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete your own account"
        )

    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.delete_user(db=db, user_id=user_id)