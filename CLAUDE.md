# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A FastAPI + PostgreSQL service for tracking store inventory: items (SKU, quantity, unit price) grouped into categories. No authentication. SQLAlchemy 2.0 (sync, `psycopg2`) for the ORM, Alembic for migrations.

## Commands

Setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # installs requirements.txt plus pytest/httpx
cp .env.example .env                  # then set DATABASE_URL to a reachable Postgres instance
alembic upgrade head
```

Run the app:

```bash
uvicorn app.main:app --reload
```

Migrations (generate after changing anything in `app/models/`):

```bash
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

Tests (in-memory SQLite, no Postgres required — see Testing below):

```bash
pytest                                    # full suite
pytest tests/test_items.py                # one file
pytest tests/test_items.py::test_get_item # one test
pytest -k "duplicate"                     # by keyword
```

## Architecture

**Layering**: `routers/` (HTTP concerns: request/response models, status codes, dependency injection) → `crud/` (all database access, takes/returns ORM models) → `models/` (SQLAlchemy ORM). `schemas/` (Pydantic) define the wire format and are distinct from the ORM models — routers convert between them via `response_model` and `from_attributes=True`. Cross-entity checks (e.g. "does this `category_id` exist?") happen in the router, not in `crud/`, by calling into the other entity's CRUD module — see `routers/items.py`.

**Primary keys are UUIDs** (`sqlalchemy.Uuid`, Python-side `default=uuid.uuid4`), not autoincrement integers. Path/query params that accept an id are typed `uuid.UUID` so FastAPI 422s on malformed ids before hitting the DB.

**Config**: `app/config.py` uses `pydantic-settings` and requires `DATABASE_URL` — there is no default, so the app (and Alembic, which imports `app.config.settings` in `alembic/env.py`) fails fast if it's unset. Tests avoid this dependency (see below).

**DB sessions**: one `Session` per request via the `get_db` FastAPI dependency (`app/database.py`); routers depend on it and never construct sessions themselves.

**Item ↔ Category eager loading**: `crud/item.py`'s `_base_query()` always `joinedload`s `Item.category`, since `ItemRead` embeds the full `CategoryRead`. Any new item query should go through this helper rather than a bare `select(Item)` to avoid N+1s or missing-relationship serialization errors.

**Testing**: `tests/conftest.py` sets `DATABASE_URL` to an in-memory SQLite URL *before* importing `app.main`, then overrides the `get_db` dependency per-test with a fresh SQLite-backed session (`StaticPool`, tables created/dropped per test via `Base.metadata`). This means the suite never touches Postgres and needs no `.env`. If you add a model, no fixture changes are needed — `Base.metadata.create_all` picks it up automatically.

**Migrations are append-only once shared**: don't hand-edit a migration that may already be applied to someone's database (local Postgres included) — add a new revision instead. The `ee753d8f1561` migration (integer → UUID primary keys) is a worked example of a data-preserving in-place column-type conversion; use it as a template for future non-trivial (non-autogenerate-safe) schema changes.

## Production-readiness gaps

This is scaffolding-stage. The following are standard for a production FastAPI service and are **not yet present** — flag them or address them as the project matures, rather than assuming they exist:

- **Structured logging & error handling**: no logging configuration and no custom exception handlers; unhandled exceptions fall through to FastAPI's default 500 response.
- **Observability**: `/health` exists but there's no separate readiness check (e.g. DB connectivity), no metrics endpoint, and no request tracing/correlation IDs.
- **CORS**: no `CORSMiddleware` configured; a browser-based client can't call this API cross-origin as-is.
- **AuthN/AuthZ**: none, by design per the README — don't add auth silently as a side effect of an unrelated change.
- **Rate limiting / request size limits**: none.
- **Pagination guardrails**: `skip`/`limit` query params exist but `limit` is unbounded — a client can request an arbitrarily large page.
- **Environment-specific settings**: a single `Settings` class with no dev/staging/prod profiles beyond whatever `.env` is loaded.
- **CI**: no `.github/workflows` — tests and migrations aren't automatically verified on push/PR.
- **Containerization**: no `Dockerfile`/`docker-compose.yml`.
- **Dependency pinning**: `requirements.txt` uses loose version ranges, not a lockfile.

When asked to "productionize" or harden part of this service, prefer addressing items from this list over inventing unrelated scope.

## Git workflow

- **Conventional Commits**: commit subjects use a `type: description` prefix (`feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `chore:`) — this is the existing convention in the repo's history and should be followed for new commits.
- **Branch naming**: `<github-username>/<short-kebab-description>`, e.g. `eochieng/add-unit-tests`.
- **No direct commits to `main`**: changes land via a feature branch and a pull request (see recent history — every change to `main` came in through a merged PR), even for small changes.
