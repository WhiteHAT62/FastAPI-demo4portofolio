import os

from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy.orm import Session

from app import models

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_hours = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str):
    return pwd_context.hash(plain)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=ACCESS_TOKEN_EXPIRE_hours)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def add_to_blacklist(db: Session, token: str, user_id: int):
    if not db.query(models.BlacklistedToken).filter_by(token=token).first():
        blacklisted = models.BlacklistedToken(
            token=token,
            user_id=user_id,
            blacklisted_at=datetime.now(timezone.utc)
        )
        db.add(blacklisted)
        db.commit()
    else:
        raise HTTPException(
            status_code=400,
            detail="Token already blacklisted"
        )

def is_blacklisted(db: Session, token: str) -> bool:
    return db.query(models.BlacklistedToken).filter_by(token=token).first() is not None

def remove_old_token(db: Session, user_id: int):
    db.query(models.BlacklistedToken).filter(models.BlacklistedToken.user_id == user_id).delete()
    db.commit()
