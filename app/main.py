from dotenv import load_dotenv
from fastapi import FastAPI
from .database import Base, engine
from app.routers import book, user, borrowed
from app.auth import login

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(borrowed.router)
app.include_router(book.router)
app.include_router(login.router)