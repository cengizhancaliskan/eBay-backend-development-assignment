from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class TableNameMixin:
    """Mixin to add table prefix to all tables."""

    @classmethod
    def get_table_name(cls, table_name: str) -> str:
        """Get table name with prefix."""
        return f"{settings.DB_TABLE_PREFIX}{table_name}"


class Base(AsyncAttrs, DeclarativeBase):
    """Base for all SQLAlchemy models."""

    pass


class BaseModel(Base, TableNameMixin):
    """Base model class with table prefix support."""

    __abstract__ = True
