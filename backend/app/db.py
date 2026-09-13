from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, event, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(__import__('os').getenv('DB_PATH', str(ROOT / 'data' / 'bilibili_monitor.db')))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@event.listens_for(engine, 'connect')
def configure_sqlite(connection, _):
    """Keep local reads/exports responsive while the collector writes snapshots."""
    cursor = connection.cursor()
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.execute('PRAGMA busy_timeout=5000')
    cursor.close()

def now() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase): pass

class Target(Base):
    __tablename__ = 'targets'
    id: Mapped[int] = mapped_column(primary_key=True)
    target_type: Mapped[str] = mapped_column(String(20), index=True)
    target_key: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(300), default='')
    description: Mapped[str] = mapped_column(String(1000), default='')
    cover_url: Mapped[str] = mapped_column(String(1000), default='')
    owner_uid: Mapped[str] = mapped_column(String(50), default='')
    interval_seconds: Mapped[int] = mapped_column(Integer, default=300)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_collect_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str] = mapped_column(String(1000), default='')
    focus_metrics: Mapped[str] = mapped_column(Text, default='')

class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey('targets.id'), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    coin_count: Mapped[int] = mapped_column(Integer, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    danmaku_count: Mapped[int] = mapped_column(Integer, default=0)
    online_count: Mapped[int | None] = mapped_column(Integer)

class UploaderSnapshot(Base):
    __tablename__ = 'uploader_snapshots'
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey('targets.id'), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    follower_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)
    video_count: Mapped[int] = mapped_column(Integer, default=0)

class CollectLog(Base):
    __tablename__ = 'collect_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey('targets.id'), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    status: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(1000), default='')

def init_db():
    Base.metadata.create_all(engine)
    # Lightweight schema upgrade for databases created by the first MVP.
    columns = {c['name'] for c in inspect(engine).get_columns('targets')}
    additions = {
        'last_success_at': 'DATETIME',
        'last_error_at': 'DATETIME',
        'next_collect_at': 'DATETIME',
        'focus_metrics': 'TEXT',
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in columns:
                connection.execute(text(f'ALTER TABLE targets ADD COLUMN {name} {sql_type}'))

def trend_rows(session: Session, model: Any, target_id: int, hours: int):
    cutoff = now() - timedelta(hours=hours)
    return list(session.scalars(select(model).where(model.target_id == target_id, model.captured_at >= cutoff).order_by(model.captured_at)))
