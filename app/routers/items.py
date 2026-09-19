import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import category as crud_category
from app.crud import item as crud_item
from app.database import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    if crud_category.get_category(db, item_in.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if crud_item.get_item_by_sku(db, item_in.sku):
        raise HTTPException(status_code=409, detail="Item with this SKU already exists")
    return crud_item.create_item(db, item_in)


@router.get("/", response_model=list[ItemRead])
def list_items(
    skip: int = 0,
    limit: int = 100,
    category_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
):
    return crud_item.get_items(db, skip=skip, limit=limit, category_id=category_id)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = crud_item.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: uuid.UUID, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = crud_item.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item_in.category_id is not None and crud_category.get_category(db, item_in.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud_item.update_item(db, item, item_in)
