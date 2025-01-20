from src.core.config import settings
from src.db.base import Base


class TableNameMixin:
    """Mixin to add table prefix to all tables."""

    @classmethod
    def get_table_name(cls, table_name: str) -> str:
        """Get table name with prefix."""
        return f"{settings.DB_TABLE_PREFIX}{table_name}"


class BaseModel(Base, TableNameMixin):
    """Base model class with table prefix support."""

    __abstract__ = True
