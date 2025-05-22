from fastapi import APIRouter

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.get("/")
def read_books():
    return [{"id": 1, "name": "Mencari Cinta Sejati"}]