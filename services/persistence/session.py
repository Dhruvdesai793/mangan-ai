"""Central SQLAlchemy engine/session lifecycle with explicit availability checks."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import Settings, get_settings

LOGGER = logging.getLogger(__name__)


class Database:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.engine: Engine = create_engine(
            self.settings.database_url,
            pool_pre_ping=True,
            pool_recycle=1800,
            future=True,
        )
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, class_=Session)

    def ping(self) -> bool:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            LOGGER.warning("database unavailable: %s", exc)
            if self.settings.mangan_database_required:
                raise
            return False

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
