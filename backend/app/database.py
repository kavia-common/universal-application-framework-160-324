from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text

from .config import get_settings


class Base(DeclarativeBase):
    pass


class ShutdownLog(Base):
    """
    Table for logging EC2 shutdown events.
    """
    __tablename__ = "ec2_shutdown_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instance_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


def _create_engine():
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    return engine


_engine = _create_engine()
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """
    Initialize database tables.
    """
    Base.metadata.create_all(bind=_engine)


@contextmanager
def db_session() -> Generator:
    """
    Provide a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
