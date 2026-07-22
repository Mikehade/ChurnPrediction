import typing as t
import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import as_declarative, declared_attr

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        index=True, unique=True, nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), default=None, nullable=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
