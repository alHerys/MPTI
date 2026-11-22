"""Database bootstrap shared by the app and scripts."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.config import database_url
from app.models import Base, make_engine, make_session_factory


class Database:
    def __init__(self, url: str | None = None):
        self.url = url or database_url()
        if self.url.startswith("sqlite:///") and not self.url.startswith("sqlite:////"):
            # Keep the SQLite file directory creatable for production runs under ./var/.
            path = Path(self.url.replace("sqlite:///", "", 1))
            if str(path.parent) not in ("", "."):
                path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = make_engine(self.url)
        Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = make_session_factory(self.engine)

    def session(self) -> Session:
        return self.session_factory()

    def healthcheck(self) -> bool:
        from sqlalchemy import text

        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
