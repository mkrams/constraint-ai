"""SQLAlchemy models for the constraint graph application."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.database import Base


def utcnow():
    """Get current UTC time."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Item(Base):
    """Engineering component that owns its own data."""

    __tablename__ = "items"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    short_id = Column(String, unique=True, nullable=False)  # e.g. "SYS-001"
    name = Column(String, nullable=False)  # e.g. "Power Supply Unit"
    item_type = Column(
        String, nullable=False
    )  # e.g. "System Requirement", "Hardware Spec"
    domain = Column(
        String, nullable=False
    )  # e.g. "electrical", "mechanical", "thermal", "software", "systems"
    description = Column(Text, nullable=True)

    # Optional Trace.Space link
    tracespace_item_id = Column(String, nullable=True)
    tracespace_org = Column(String, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    parameters = relationship(
        "Parameter", back_populates="item", cascade="all, delete-orphan"
    )
    source_traces = relationship(
        "Trace",
        foreign_keys="Trace.source_item_id",
        back_populates="source_item",
        cascade="all, delete-orphan",
    )
    target_traces = relationship(
        "Trace",
        foreign_keys="Trace.target_item_id",
        back_populates="target_item",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Item {self.short_id}: {self.name}>"


class Parameter(Base):
    """Parameter belonging to an item."""

    __tablename__ = "parameters"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g. "Max Power Output"
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # e.g. "W", "V", "°C"
    param_type = Column(String, default="parameter")  # matches Trace.Space field type

    # Optional Trace.Space link
    tracespace_field_name = Column(String, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    item = relationship("Item", back_populates="parameters")

    def __repr__(self):
        return f"<Parameter {self.name}: {self.value} {self.unit}>"


class Trace(Base):
    """Relationship between items."""

    __tablename__ = "traces"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    source_item_id = Column(String, ForeignKey("items.id"), nullable=False)
    target_item_id = Column(String, ForeignKey("items.id"), nullable=False)
    trace_type = Column(
        String, nullable=False
    )  # e.g. "powers", "cooled_by", "depends_on"
    description = Column(Text, nullable=True)

    # Optional Trace.Space link
    tracespace_trace_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    source_item = relationship(
        "Item", foreign_keys=[source_item_id], back_populates="source_traces"
    )
    target_item = relationship(
        "Item", foreign_keys=[target_item_id], back_populates="target_traces"
    )

    def __repr__(self):
        return f"<Trace {self.source_item_id} -[{self.trace_type}]-> {self.target_item_id}>"


class Constraint(Base):
    """Core constraint entity for the graph."""

    __tablename__ = "constraints"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)  # e.g. "Power Budget"
    description = Column(Text, nullable=True)  # human description
    rule_type = Column(
        String, nullable=False
    )  # "lte", "gte", "eq", "lt", "gt", "range", "sum_lte", "sum_gte", "ratio_lte", "tolerance"
    severity = Column(
        String, default="error"
    )  # "critical", "error", "warning", "info"
    expression = Column(Text, nullable=True)  # optional custom expression

    # For simple binary constraints (source op target):
    source_parameter_id = Column(String, ForeignKey("parameters.id"), nullable=True)
    target_parameter_id = Column(String, ForeignKey("parameters.id"), nullable=True)

    # For range constraints:
    range_min = Column(Float, nullable=True)
    range_max = Column(Float, nullable=True)

    # For tolerance constraints:
    tolerance_value = Column(Float, nullable=True)

    # For ratio constraints:
    ratio_limit = Column(Float, nullable=True)

    # Cross-domain descriptions (JSON dict)
    domain_descriptions = Column(JSON, nullable=True, default=dict)

    # AI-generated explanation cache
    ai_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    sources = relationship(
        "ConstraintSource",
        foreign_keys="ConstraintSource.constraint_id",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Constraint {self.name}: {self.rule_type}>"


class ConstraintSource(Base):
    """Source parameters for multi-source constraints (e.g., sum_lte)."""

    __tablename__ = "constraint_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    constraint_id = Column(String, ForeignKey("constraints.id"), nullable=False)
    parameter_id = Column(String, ForeignKey("parameters.id"), nullable=False)
    role = Column(String, default="source")  # "source" or "target"

    created_at = Column(DateTime, default=utcnow)

    def __repr__(self):
        return f"<ConstraintSource constraint={self.constraint_id}, param={self.parameter_id}>"


class EvaluationResult(Base):
    """Cached constraint evaluation results."""

    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    constraint_id = Column(String, ForeignKey("constraints.id"), nullable=False)
    status = Column(
        String, nullable=False
    )  # "pass", "fail", "warning", "unknown"
    actual_value = Column(Float, nullable=True)
    limit_value = Column(Float, nullable=True)
    margin = Column(Float, nullable=True)  # percentage
    margin_absolute = Column(Float, nullable=True)  # absolute value
    message = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=utcnow)

    def __repr__(self):
        return f"<EvaluationResult constraint={self.constraint_id}, status={self.status}>"
