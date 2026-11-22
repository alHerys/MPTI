"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import is_production, secret_key, validate_production_settings
from app.db import Database


def create_app(database_url: str | None = None, seed: bool = True, startup_check: bool = True) -> FastAPI:
    if startup_check:
        validate_production_settings()
    db = Database(database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if seed:
            from scripts.seed_demo import seed_demo

            with db.session() as session:
                seed_demo(session)
        yield

    app = FastAPI(title="ColdStart Kitchen", lifespan=lifespan)
    app.state.db = db
    app.state.lifespan_disabled = not seed

    key = secret_key() or "dev-secret-coldstart-kitchen"
    app.add_middleware(
        SessionMiddleware,
        secret_key=key,
        same_site="lax",
        https_only=is_production(),
        session_cookie="coldstart_session",
    )

    static_dir = Path("app/static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    from app.routers import auth as auth_router
    from app.routers import businesses as businesses_router
    from app.routers import pages as pages_router
    from app.routers import recommendations as rec_router
    from app.routers import sales as sales_router

    app.include_router(auth_router.router)
    app.include_router(businesses_router.router)
    app.include_router(sales_router.router)
    app.include_router(rec_router.router)
    app.include_router(pages_router.router)
    return app


app = create_app()
