import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def _base_query() -> Select[tuple[Item]]:
    return select(Item).options(joinedload(Item.category))


def get_item(db: Session, item_id: uuid.UUID) -> Item | None:
    return db.scalar(_base_query().where(Item.id == item_id))


def get_item_by_sku(db: Session, sku: str) -> Item | None:
    return db.scalar(_base_query().where(Item.sku == sku))


def get_items(
    db: Session, skip: int = 0, limit: int = 100, category_id: uuid.UUID | None = None
) -> list[Item]:
    stmt = _base_query().order_by(Item.name).offset(skip).limit(limit)
    if category_id is not None:
        stmt = stmt.where(Item.category_id == category_id)
    return list(db.scalars(stmt).unique())


def create_item(db: Session, item_in: ItemCreate) -> Item:
    item = Item(**item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return get_item(db, item.id)


def update_item(db: Session, item: Item, item_in: ItemUpdate) -> Item:
    for field, value in item_in.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return get_item(db, item.id)
