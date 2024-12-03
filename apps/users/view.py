
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/hii")
def hi_root():
    return {"hi": "how are yiu "}


@router.get("/bye")
def by_root():  
    return {"by": "Goodby "}