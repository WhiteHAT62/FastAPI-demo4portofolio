import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)

    # relasi ke Borrowed
    borrowed_books = relationship("Borrowed", back_populates="user")

class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    date = Column(Date, default=None)
    stock = Column(Integer, default=0)

    # relasi ke Borrowed
    borrowed_by = relationship("Borrowed", back_populates="book")

class Borrowed(Base):
    __tablename__ = "borrowed"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("book.id"))
    date_borrowed = Column(Date, nullable=False)
    date_due = Column(Date, nullable=False)

    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_by")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String, unique=True, nullable=False)
    blacklisted_at = Column(DateTime)