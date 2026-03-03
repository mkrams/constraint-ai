"""Pydantic schemas for request/response validation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ==================== Parameter Schemas ====================


class ParameterCreate(BaseModel):
    """Schema for creating a parameter."""

    item_id: str
    name: str
    value: float
    unit: str
    param_type: str = "parameter"
    tracespace_field_name: Optional[str] = None


class ParameterUpdate(BaseModel):
    """Schema for updating a parameter."""

    name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    param_type: Optional[str] = None
    tracespace_field_name: Optional[str] = None


class ParameterValueUpdate(BaseModel):
    """Schema for quick value-only updates."""

    value: float


class ParameterResponse(BaseModel):
    """Schema for parameter response."""

    id: str
    item_id: str
    name: str
    value: float
    unit: str
    param_type: str
    tracespace_field_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Item Schemas ====================


class ItemCreate(BaseModel):
    """Schema for creating an item."""

    short_id: str
    name: str
    item_type: str
    domain: str
    description: Optional[str] = None
    tracespace_item_id: Optional[str] = None
    tracespace_org: Optional[str] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    short_id: Optional[str] = None
    name: Optional[str] = None
    item_type: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    tracespace_item_id: Optional[str] = None
    tracespace_org: Optional[str] = None


class ItemResponse(BaseModel):
    """Schema for item response without parameters."""

    id: str
    short_id: str
    name: str
    item_type: str
    domain: str
    description: Optional[str]
    tracespace_item_id: Optional[str]
    tracespace_org: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemDetailResponse(ItemResponse):
    """Schema for detailed item response with parameters."""

    parameters: List[ParameterResponse] = []

    class Config:
        from_attributes = True


# ==================== Trace Schemas ====================


class TraceCreate(BaseModel):
    """Schema for creating a trace."""

    source_item_id: str
    target_item_id: str
    trace_type: str
    description: Optional[str] = None
    tracespace_trace_id: Optional[str] = None


class TraceUpdate(BaseModel):
    """Schema for updating a trace."""

    trace_type: Optional[str] = None
    description: Optional[str] = None
    tracespace_trace_id: Optional[str] = None


class TraceResponse(BaseModel):
    """Schema for trace response."""

    id: str
    source_item_id: str
    target_item_id: str
    trace_type: str
    description: Optional[str]
    tracespace_trace_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Constraint Schemas ====================


class ConstraintSourceCreate(BaseModel):
    """Schema for constraint source."""

    parameter_id: str
    role: str = "source"


VALID_RULE_TYPES = {"lte", "gte", "eq", "lt", "gt", "range", "sum_lte", "sum_gte", "ratio_lte", "tolerance"}
VALID_SEVERITIES = {"critical", "error", "warning", "info"}


class ConstraintCreate(BaseModel):
    """Schema for creating a constraint."""

    name: str
    description: Optional[str] = None
    rule_type: str
    severity: str = "error"

    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v: str) -> str:
        if v not in VALID_RULE_TYPES:
            raise ValueError(f"Invalid rule_type '{v}'. Must be one of: {', '.join(sorted(VALID_RULE_TYPES))}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity '{v}'. Must be one of: {', '.join(sorted(VALID_SEVERITIES))}")
        return v
    expression: Optional[str] = None
    source_parameter_id: Optional[str] = None
    target_parameter_id: Optional[str] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    tolerance_value: Optional[float] = None
    ratio_limit: Optional[float] = None
    domain_descriptions: Optional[Dict[str, str]] = None
    sources: Optional[List[ConstraintSourceCreate]] = None


class ConstraintUpdate(BaseModel):
    """Schema for updating a constraint."""

    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    severity: Optional[str] = None
    expression: Optional[str] = None
    source_parameter_id: Optional[str] = None
    target_parameter_id: Optional[str] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    tolerance_value: Optional[float] = None
    ratio_limit: Optional[float] = None
    domain_descriptions: Optional[Dict[str, str]] = None


class ConstraintSourceResponse(BaseModel):
    """Schema for constraint source response."""

    id: str
    constraint_id: str
    parameter_id: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResultResponse(BaseModel):
    """Schema for evaluation result response."""

    id: str
    constraint_id: str
    status: str
    actual_value: Optional[float]
    limit_value: Optional[float]
    margin: Optional[float]
    margin_absolute: Optional[float]
    message: Optional[str]
    evaluated_at: datetime

    class Config:
        from_attributes = True


class ConstraintResponse(BaseModel):
    """Schema for constraint response."""

    id: str
    name: str
    description: Optional[str]
    rule_type: str
    severity: str
    expression: Optional[str]
    source_parameter_id: Optional[str]
    target_parameter_id: Optional[str]
    range_min: Optional[float]
    range_max: Optional[float]
    tolerance_value: Optional[float]
    ratio_limit: Optional[float]
    domain_descriptions: Optional[Dict[str, Any]]
    ai_explanation: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConstraintDetailResponse(ConstraintResponse):
    """Schema for detailed constraint response with evaluation results."""

    sources: List[ConstraintSourceResponse] = []
    latest_result: Optional[EvaluationResultResponse] = None

    class Config:
        from_attributes = True


# ==================== Engine Schemas ====================


class WhatIfRequest(BaseModel):
    """Schema for what-if analysis request."""

    parameter_id: str
    proposed_value: float


class ImpactAnalysis(BaseModel):
    """Schema for impact analysis result."""

    parameter_id: str
    parameter_name: str
    current_value: float
    proposed_value: float
    affected_constraints: List[Dict[str, Any]] = []
    feasible: bool = True
    message: str = ""


class ParameterImpactDetail(BaseModel):
    """Schema for detailed impact on a single parameter."""

    parameter_id: str
    parameter_name: str
    current_value: float
    recommended_value: Optional[float] = None
    constraints_affected: int = 0
    constraints_failing: int = 0


class DownstreamImpact(BaseModel):
    """Schema for downstream impact analysis."""

    primary_parameter: ParameterImpactDetail
    downstream_impacts: List[ParameterImpactDetail] = []
    summary: str = ""


class FeasibleRangeResponse(BaseModel):
    """Schema for feasible range response."""

    parameter_id: str
    parameter_name: str
    current_value: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    margin_to_min: Optional[float] = None
    margin_to_max: Optional[float] = None
    unit: str


class SensitivityAnalysis(BaseModel):
    """Schema for sensitivity analysis."""

    parameter_id: str
    parameter_name: str
    constraints_sensitive_to_change: List[Dict[str, Any]] = []
    tightest_constraint: Optional[Dict[str, Any]] = None


class ConstraintMargin(BaseModel):
    """Schema for constraint margin."""

    constraint_id: str
    constraint_name: str
    rule_type: str
    status: str
    margin_percentage: Optional[float]
    margin_absolute: Optional[float]
    actual_value: Optional[float]
    limit_value: Optional[float]


class MarginReport(BaseModel):
    """Schema for margin report."""

    total_constraints: int
    passing_constraints: int
    failing_constraints: int
    warning_constraints: int
    constraints_by_margin: List[ConstraintMargin] = []


class SystemHealthResponse(BaseModel):
    """Schema for system health summary."""

    total_items: int
    total_parameters: int
    total_constraints: int
    total_traces: int
    passing_constraints: int
    failing_constraints: int
    warning_constraints: int
    health_percentage: float
    critical_issues: List[Dict[str, Any]] = []


class EvaluateAllResponse(BaseModel):
    """Schema for evaluate all constraints response."""

    total_constraints: int
    passed: int
    failed: int
    warnings: int
    evaluation_timestamp: datetime
    results: List[EvaluationResultResponse] = []


# ==================== Trace.Space Schemas ====================


class TraceSpaceConnect(BaseModel):
    """Schema for Trace.Space connection."""

    client_id: str
    client_secret: str
    org: str


class LinkParameterRequest(BaseModel):
    """Schema for linking a parameter to Trace.Space."""

    parameter_id: str
    tracespace_field_name: str
    tracespace_item_id: str


class SyncRequest(BaseModel):
    """Schema for sync request."""

    parameter_ids: Optional[List[str]] = None  # None = sync all
