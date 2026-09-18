from fastapi import FastAPI

from app.config import settings
from app.routers import categories, items

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(categories.router)
app.include_router(items.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
