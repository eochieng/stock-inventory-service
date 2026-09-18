from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryRead


class ItemBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    quantity: int = Field(0, ge=0)
    unit_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    category_id: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    sku: str | None = Field(None, min_length=1, max_length=64)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    quantity: int | None = Field(None, ge=0)
    unit_price: Decimal | None = Field(None, ge=0, max_digits=10, decimal_places=2)
    category_id: int | None = None


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryRead
