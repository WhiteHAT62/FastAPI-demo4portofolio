from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, database, crud
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/borrowed",
    tags=["borrowed"]
)

@router.post("/create", response_model=schemas.BorrowedResponse)
def create_borrowed(
    borrowed: schemas.BorrowedCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: User must be logged in to borrow books"
        )

    book = crud.get_book(db=db, info=borrowed.book_id)
    if not book or book[0].stock <= 0:
        raise HTTPException(
            status_code=400,
            detail="Book is out of stock and cannot be borrowed"
        )

    book[0].stock -= 1
    db.commit()
    db.refresh(book[0])

    return crud.create_borrowed(db=db, borrowed=borrowed)

@router.get("/user/{user_id}", response_model=list[schemas.BorrowedResponse])
def get_borrowed_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this user's borrowed books"
        )

    return crud.get_borrowed_records(db=db, user_id=user_id, skip=skip, limit=limit)

@router.get("/book/{book_id}", response_model=list[schemas.BorrowedResponse])
def get_borrowed_by_book(
    book_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access borrowed records by book"
        )

    borrowed = crud.get_borrowed_records(db=db, book_id=book_id, skip=skip, limit=limit)
    if not borrowed:
        raise HTTPException(status_code=404, detail="No borrowed records found for this book")

    return borrowed


@router.delete("/{borrowed_id}/return")
def return_borrowed(
    borrowed_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role == "admin":
        borrowed = crud.get_borrowed(db=db, borrowed_id=borrowed_id)
        if not borrowed:
            raise HTTPException(status_code=404, detail="Borrowed record not found")

        book = crud.get_book(db=db, info=borrowed["book_id"])
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        book[0].stock += 1
        db.commit()
        db.refresh(book[0])

        return crud.delete_borrowed(db=db, borrowed_id=borrowed_id)

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to return borrowed books"
        )