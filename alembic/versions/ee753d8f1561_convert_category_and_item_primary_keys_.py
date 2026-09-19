"""convert category and item primary keys to uuid

Revision ID: ee753d8f1561
Revises: 6a1ad2c06d31
Create Date: 2026-09-18 16:54:39.811541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee753d8f1561'
down_revision: Union[str, Sequence[str], None] = '6a1ad2c06d31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add UUID columns, backfilled per-row for any existing data.
    op.add_column(
        "categories",
        sa.Column("new_id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
    )
    op.add_column(
        "items",
        sa.Column("new_id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
    )
    op.add_column("items", sa.Column("new_category_id", sa.Uuid(), nullable=True))

    # Remap the items -> categories relationship onto the new UUID keys.
    op.execute(
        "UPDATE items SET new_category_id = categories.new_id "
        "FROM categories WHERE items.category_id = categories.id"
    )
    op.alter_column("items", "new_category_id", nullable=False)

    # Swap categories.id for its UUID column.
    op.drop_constraint("items_category_id_fkey", "items", type_="foreignkey")
    op.drop_constraint("categories_pkey", "categories", type_="primary")
    op.drop_column("categories", "id")
    op.alter_column("categories", "new_id", new_column_name="id", server_default=None)
    op.create_primary_key("categories_pkey", "categories", ["id"])

    # Swap items.id and items.category_id for their UUID columns.
    op.drop_constraint("items_pkey", "items", type_="primary")
    op.drop_index("ix_items_category_id", table_name="items")
    op.drop_column("items", "id")
    op.drop_column("items", "category_id")
    op.alter_column("items", "new_id", new_column_name="id", server_default=None)
    op.alter_column("items", "new_category_id", new_column_name="category_id")
    op.create_primary_key("items_pkey", "items", ["id"])
    op.create_index("ix_items_category_id", "items", ["category_id"])
    op.create_foreign_key(
        "items_category_id_fkey",
        "items",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("items_category_id_fkey", "items", type_="foreignkey")
    op.drop_index("ix_items_category_id", table_name="items")
    op.drop_constraint("items_pkey", "items", type_="primary")
    op.drop_constraint("categories_pkey", "categories", type_="primary")

    # Re-add integer columns (new sequential ids; original integer values are not restored).
    op.execute("ALTER TABLE categories ADD COLUMN old_id SERIAL")
    op.execute("ALTER TABLE items ADD COLUMN old_id SERIAL")
    op.add_column("items", sa.Column("old_category_id", sa.Integer(), nullable=True))

    op.execute(
        "UPDATE items SET old_category_id = categories.old_id "
        "FROM categories WHERE items.category_id = categories.id"
    )
    op.alter_column("items", "old_category_id", nullable=False)

    op.drop_column("categories", "id")
    op.alter_column("categories", "old_id", new_column_name="id")
    op.create_primary_key("categories_pkey", "categories", ["id"])

    op.drop_column("items", "id")
    op.drop_column("items", "category_id")
    op.alter_column("items", "old_id", new_column_name="id")
    op.alter_column("items", "old_category_id", new_column_name="category_id")
    op.create_primary_key("items_pkey", "items", ["id"])
    op.create_index("ix_items_category_id", "items", ["category_id"])
    op.create_foreign_key(
        "items_category_id_fkey",
        "items",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )
