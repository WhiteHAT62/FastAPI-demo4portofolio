from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app import schemas, database, crud
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/buku/create", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(database.get_db),
                current_user: schemas.User = Depends(get_current_user)
                ):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource"
        )
    return crud.create_book(db=db, book=book)


@router.get("/{book_info}", response_model=list[schemas.BookResponse])
def read_books(
        book_info: str = Path(..., description="ID buku atau keyword judul/pengarang"),
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(database.get_db),
):
    try:
        parsed_info: Union[int, str] = int(book_info)
    except ValueError:
        parsed_info = book_info

    books = crud.get_book(db=db, info=parsed_info, skip=skip, limit=limit)

    if not books:
        if isinstance(parsed_info, int):
            raise HTTPException(
                status_code=404,
                detail=f"Buku dengan id '{parsed_info}' tidak ditemukan."
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Tidak ada buku yang ditemukan dengan keyword '{parsed_info}'."
            )
    return books


@router.put("/{book_info}/update", response_model=schemas.BookResponse)
def update_book(
        book_info: int,
        book_update: schemas.BookUpdate,
        db: Session = Depends(database.get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource"
        )
    updated_book = crud.update_book(db=db, book_id=book_info, book_update=book_update)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@router.delete("/{book_info}/delete")
def delete_book(
        book_info: int,
        db: Session = Depends(database.get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource"
        )
    book = crud.get_book(db=db, info=book_info)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return crud.delete_book(db=db, book_id=book_info)