# Stock Inventory Service

A FastAPI + PostgreSQL service for tracking store inventory: items (SKU, quantity, unit price) grouped into categories, with endpoints to add and update inventory records. No authentication.

## Stack

- FastAPI
- SQLAlchemy 2.0 (sync, `psycopg2`)
- Alembic for migrations
- PostgreSQL

## Setup

1. Make sure you have a reachable PostgreSQL instance and create a database:

   ```bash
   createdb stock_inventory
   ```

2. Create a virtualenv and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   # edit .env and set DATABASE_URL to point at your Postgres instance
   ```

4. Run migrations:

   ```bash
   alembic upgrade head
   ```

5. Run the app:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open the interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API

### Categories (`/categories`)

| Method | Path | Description |
|---|---|---|
| POST | `/categories/` | Create a category |
| GET | `/categories/` | List categories |

### Items (`/items`)

| Method | Path | Description |
|---|---|---|
| POST | `/items/` | Create an inventory item |
| GET | `/items/` | List items (optional `category_id` filter) |
| GET | `/items/{item_id}` | Get a single item |
| PATCH | `/items/{item_id}` | Partially update an item (e.g. adjust `quantity`) |

### Example

```bash
curl -X POST http://127.0.0.1:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Beverages"}'

curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"sku": "BEV-001", "name": "Cola 12oz", "quantity": 100, "unit_price": 1.50, "category_id": 1}'

curl -X PATCH http://127.0.0.1:8000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 90}'
```

## Schema

- **Category**: `id`, `name` (unique), `description`, `created_at`, `updated_at`
- **Item**: `id`, `sku` (unique), `name`, `description`, `quantity` (>= 0), `unit_price` (>= 0), `category_id` (FK), `created_at`, `updated_at`

## Testing

Install dev dependencies and run the unit test suite (uses an in-memory SQLite database, no Postgres required):

```bash
pip install -r requirements-dev.txt
pytest
```

## Migrations

Generate a new migration after changing models in `app/models/`:

```bash
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```
