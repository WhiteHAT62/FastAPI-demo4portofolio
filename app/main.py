from dotenv import load_dotenv
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import book, user
from app.auth import auth

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(book.router)
app.include_router(auth.router)
