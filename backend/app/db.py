
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "students" in inspector.get_table_names():
            existing_cols = [c["name"] for c in inspector.get_columns("students")]
            new_columns = [
                ("phone", "VARCHAR(50)"),
                ("linkedin_url", "VARCHAR(300)"),
                ("github_url", "VARCHAR(300)"),
                ("hackerrank_url", "VARCHAR(300)"),
                ("leetcode_url", "VARCHAR(300)"),
                ("portfolio_url", "VARCHAR(300)"),
                ("bio", "TEXT"),
            ]
            for col_name, col_type in new_columns:
                if col_name not in existing_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE students ADD COLUMN {col_name} {col_type} DEFAULT ''"))
                        conn.commit()
                    except Exception:
                        pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()