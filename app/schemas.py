from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr

# User schema
class UserBase(BaseModel):
    name: str
    username: str
    password: str
    address: str
    phone: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordUpdate(BaseModel):
    password: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    address: str
    phone: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

# Book schema
class BookBase(BaseModel):
    name: str
    author: str
    isbn: str
    date: date
    stock: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True

# Borrowed schema
class BorrowedBase(BaseModel):
    user_id: int
    book_id: int
    date_borrowed: date
    date_due: date

class BorrowedCreate(BorrowedBase):
    pass

class Borrowed(BorrowedBase):
    id: int

    class Config:
        from_attributes = True

# login schema
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str