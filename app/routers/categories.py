from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import category as crud_category
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    if crud_category.get_category_by_name(db, category_in.name):
        raise HTTPException(status_code=409, detail="Category with this name already exists")
    return crud_category.create_category(db, category_in)


@router.get("/", response_model=list[CategoryRead])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_category.get_categories(db, skip=skip, limit=limit)
