# -*- coding: utf-8 -*-
"""SQLite 数据库连接与 ORM 基类。"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},   # SQLite + FastAPI 多线程需要
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate_columns():
    """轻量列迁移：SQLite 的 create_all 不会给已有表加列，这里补齐。

    v2.0 新增：grade_records.source_id / batch_no / suggested_price
    """
    wanted = {
        "grade_records": [
            ("source_id", "ALTER TABLE grade_records ADD COLUMN source_id INTEGER"),
            ("batch_no", "ALTER TABLE grade_records ADD COLUMN batch_no VARCHAR(60)"),
            ("suggested_price", "ALTER TABLE grade_records ADD COLUMN suggested_price FLOAT"),
        ],
    }
    with engine.begin() as conn:
        for table, cols in wanted.items():
            existing = {
                row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            }
            for name, ddl in cols:
                if name not in existing:
                    conn.execute(text(ddl))


def init_db():
    import app.models_db  # 确保表模型已注册
    Base.metadata.create_all(bind=engine)
    _migrate_columns()
