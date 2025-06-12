from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

import sqlalchemy as sa
import datetime

try:
    from db.db import db
except ImportError:
    from .db import db


class BaseModel(db.Model):
    """Base model class for all database models."""
    __abstract__ = True  # Makes it so the table isnt created

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

    def to_dict(self):
        result_dict = {}
        # Ability to hide certain fields from the output
        hidden_fields = set(getattr(self, "__hidden_fields__", set()))

        for column in self.__table__.columns:
            # Skip foreign key columns and hidden fields
            if column.foreign_keys or column.name in hidden_fields:
                continue

            value = getattr(self, column.name)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            result_dict[column.name] = value

        # Add related objects to the dictionary
        for rel in self.__mapper__.relationships:
            related_obj = getattr(self, rel.key)
            if related_obj is not None:
                result_dict[rel.key] = related_obj.to_dict()
            else:
                result_dict[rel.key] = None

        return result_dict


class Metadata(BaseModel):
    """Model representing metadata of a file."""
    __tablename__ = "metadata"
    __hidden_fields__ = {"ip_address"}

    # Note: UUIDs are not natively supported by SQLite
    id: Mapped[str] = mapped_column(
        sa.String(36),
        primary_key=True
    )
    ip_address: Mapped[str | None] = mapped_column(nullable=True, index=True)
    filename: Mapped[str]
    time_created: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime, index=True, default=func.now()
    )

    hostname_id: Mapped[int | None] =\
        mapped_column(sa.ForeignKey("hostname.id"), nullable=True, index=True)
    hostname: Mapped[Hostname | None] = relationship("Hostname")

    benchmark_id: Mapped[int | None] =\
        mapped_column(sa.ForeignKey("benchmark.id"), nullable=True, index=True)
    benchmark: Mapped[Benchmark | None] = relationship("Benchmark")

    result_id: Mapped[int | None] =\
        mapped_column(sa.ForeignKey("result.id"),
                      nullable=True, index=True)
    result: Mapped[Result | None] = relationship("Result")

    department_id: Mapped[int | None] =\
        mapped_column(sa.ForeignKey("department.id"),
                      nullable=True, index=True)
    department: Mapped[Department | None] = relationship("Department")


class Benchmark(BaseModel):
    __tablename__ = "benchmark"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class Department(BaseModel):
    __tablename__ = "department"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    # Relationship to department users
    users: Mapped[list["DepartmentUser"]] = relationship(
        "DepartmentUser",
        back_populates="department",
        cascade="all, delete-orphan"
    )


class Result(BaseModel):
    __tablename__ = "result"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class Hostname(BaseModel):
    __tablename__ = "hostname"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class DepartmentUser(BaseModel):
    """Association table for department-user relationships"""
    __tablename__ = "department_user"

    __hidden_fields__ = {"users"}

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(
        sa.ForeignKey("department.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_handle: Mapped[str] = mapped_column(nullable=False, index=True)

    # Relationship to department
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="users"
    )

    # Ensure unique combination of department and user
    __table_args__ = (
        sa.UniqueConstraint('department_id', 'user_handle',
                            name='_department_user_uc'),
    )
