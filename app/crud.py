from typing import Optional, Union

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth.utils import hash_password, verify_password


# User
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password

    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user
    return None


def get_users(db: Session, skip: int = 0, limit: int = 10):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, password_update: schemas.PasswordUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    if not verify_password(password_update.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    hashed_password = hash_password(password_update.new_password)
    db_user.password = hashed_password
    db.commit()
    db.refresh(db_user)
    return {"message": "Password updated successfully"}


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return {"message": "User Deleted successfully"}


# Book
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book(db: Session, info: Optional[Union[int, str]], skip: int = 0, limit: int = 10):
    query = db.query(models.Book)

    if isinstance(info, int):
        query = query.filter(models.Book.id == info)
    elif isinstance(info, str):
        like_pattern = f"%{info}%"
        query = query.filter(
            or_(
                models.Book.name.ilike(like_pattern),
                models.Book.author.ilike(like_pattern)
            )
        )

    return query.offset(skip).limit(limit).all()


def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if db_book:
        for key, value in book_update.model_dump(exclude_unset=True).items():
            setattr(db_book, key, value)

        db.commit()
        db.refresh(db_book)
        return db_book

    else:
        return None


def delete_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None
    db.delete(book)
    db.commit()
    return {"message": "Book Deleted successfully"}


# Borrowed
def create_borrowed(db: Session, borrowed: schemas.BorrowedCreate):
    db_borrowed = models.Borrowed(**borrowed.model_dump())
    db.add(db_borrowed)
    db.commit()
    db.refresh(db_borrowed)
    user = db.query(models.User).filter(models.User.id == db_borrowed.user_id).first()
    book = db.query(models.Book).filter(models.Book.id == db_borrowed.book_id).first()
    return {
        "id": db_borrowed.id,
        "user": user.name if user else None,
        "book": book.name if book else None,
        "date_borrowed": db_borrowed.date_borrowed,
        "date_due": db_borrowed.date_due
    }


def get_borrowed_records(db: Session, book_id: int = None, user_id: int = None, skip: int = 0, limit: int = 10):
    query = db.query(models.Borrowed)
    if book_id is not None:
        query = query.filter(models.Borrowed.book_id == book_id)
    if user_id is not None:
        query = query.filter(models.Borrowed.user_id == user_id)
    borrowed = query.offset(skip).limit(limit).all()
    result = []
    for b in borrowed:
        user = db.query(models.User).filter(models.User.id == b.user_id).first()
        book = db.query(models.Book).filter(models.Book.id == b.book_id).first()
        result.append({
            "id": b.id,
            "user": user.name if user else None,
            "book": book.name if book else None,
            "date_borrowed": b.date_borrowed,
            "date_due": b.date_due
        })
    return result


def delete_borrowed(db: Session, borrowed_id: int):
    borrowed = db.query(models.Borrowed).filter(models.Borrowed.id == borrowed_id).first()
    if not borrowed:
        return None
    db.delete(borrowed)
    db.commit()
    return {"message": "Borrowed record deleted successfully"}


def get_borrowed(db, borrowed_id):
    borrowed = db.query(models.Borrowed).filter(models.Borrowed.id == borrowed_id).first()
    if not borrowed:
        return None
    return {
        "id": borrowed.id,
        "user_id": borrowed.user_id,
        "book_id": borrowed.book_id,
        "date_borrowed": borrowed.date_borrowed,
        "date_due": borrowed.date_due
    }
