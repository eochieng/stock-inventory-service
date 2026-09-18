from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    stmt = select(Category).order_by(Category.name).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    category = Category(**category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, category_in: CategoryUpdate) -> Category:
    for field, value in category_in.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category
