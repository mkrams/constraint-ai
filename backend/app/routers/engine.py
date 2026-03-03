"""API router for constraint evaluation engine and analysis."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Parameter, Constraint, EvaluationResult, Item
from app.models.schemas import (
    WhatIfRequest,
    ImpactAnalysis,
    DownstreamImpact,
    FeasibleRangeResponse,
    SensitivityAnalysis,
    MarginReport,
    ConstraintMargin,
    SystemHealthResponse,
    EvaluateAllResponse,
)
from app.engine.evaluator import evaluate_all_constraints, evaluate_constraint
from app.engine.propagation import analyze_change_impact, analyze_full_impact
from app.engine.feasibility import get_feasible_range

router = APIRouter(prefix="/api/engine", tags=["engine"])


@router.post("/evaluate-all", response_model=EvaluateAllResponse)
def evaluate_all_constraints_endpoint(db: Session = Depends(get_db)):
    """Evaluate all constraints and store results."""
    results = evaluate_all_constraints(db)

    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    warnings = sum(1 for r in results if r.status == "warning")

    return {
        "total_constraints": len(results),
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "evaluation_timestamp": results[0].evaluated_at if results else None,
        "results": results,
    }


@router.post("/what-if", response_model=ImpactAnalysis)
def what_if_analysis(request: WhatIfRequest, db: Session = Depends(get_db)):
    """Analyze impact of parameter change WITHOUT modifying database."""
    param = db.query(Parameter).filter(Parameter.id == request.parameter_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    impact = analyze_change_impact(request.parameter_id, request.proposed_value, db)

    if "error" in impact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=impact["error"])

    return {
        "parameter_id": request.parameter_id,
        "parameter_name": param.name,
        "current_value": param.value,
        "proposed_value": request.proposed_value,
        "feasible": impact.get("feasible", False),
        "message": impact.get("summary", ""),
        "affected_constraints": impact.get("affected_constraints", []),
    }


@router.post("/change-impact", response_model=DownstreamImpact)
def change_impact_analysis(request: WhatIfRequest, db: Session = Depends(get_db)):
    """Analyze full downstream impact of parameter change."""
    param = db.query(Parameter).filter(Parameter.id == request.parameter_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    full_impact = analyze_full_impact(request.parameter_id, request.proposed_value, db)

    if "error" in full_impact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=full_impact["error"])

    return {
        "primary_parameter": {
            "parameter_id": request.parameter_id,
            "parameter_name": param.name,
            "current_value": param.value,
            "recommended_value": request.proposed_value if full_impact.get("feasible_without_changes") else None,
            "constraints_affected": len(full_impact.get("primary_parameter", {}).get("affected_constraints", [])),
            "constraints_failing": len(full_impact.get("primary_parameter", {}).get("newly_failing", [])),
        },
        "downstream_impacts": [
            {
                "parameter_id": impact["parameter_id"],
                "parameter_name": impact["parameter_name"],
                "current_value": impact["current_value"],
                "recommended_value": impact.get("required_value"),
                "constraints_affected": 1,
                "constraints_failing": 0,
            }
            for impact in full_impact.get("cascading_impacts", [])
        ],
        "summary": f"{'Feasible' if full_impact.get('feasible_without_changes') else 'Not feasible'} without changes. "
        f"{'Feasible with' if full_impact.get('feasible_with_changes') else 'Not feasible even with'} downstream adjustments.",
    }


@router.get("/feasibility/{parameter_id}", response_model=FeasibleRangeResponse)
def get_feasibility_range(parameter_id: str, db: Session = Depends(get_db)):
    """Get feasible range for a parameter given all constraints."""
    param = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    range_info = get_feasible_range(parameter_id, db)

    if not range_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not calculate feasible range",
        )

    return {
        "parameter_id": parameter_id,
        "parameter_name": param.name,
        "current_value": param.value,
        "min_value": range_info.get("min_value", float("-inf")),
        "max_value": range_info.get("max_value", float("inf")),
        "margin_to_min": range_info.get("margin_to_min", 0),
        "margin_to_max": range_info.get("margin_to_max", 0),
        "unit": param.unit,
    }


@router.get("/sensitivity/{parameter_id}", response_model=SensitivityAnalysis)
def sensitivity_analysis(parameter_id: str, db: Session = Depends(get_db)):
    """Analyze which constraints are most sensitive to parameter changes."""
    param = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    # Find all constraints involving this parameter
    constraints = (
        db.query(Constraint)
        .filter(
            (Constraint.source_parameter_id == parameter_id)
            | (Constraint.target_parameter_id == parameter_id)
        )
        .all()
    )

    sensitive_constraints = []
    tightest = None
    tightest_margin = float("inf")

    for constraint in constraints:
        # Get latest evaluation
        latest = (
            db.query(EvaluationResult)
            .filter(EvaluationResult.constraint_id == constraint.id)
            .order_by(EvaluationResult.evaluated_at.desc())
            .first()
        )

        if latest:
            constraint_info = {
                "constraint_id": constraint.id,
                "constraint_name": constraint.name,
                "rule_type": constraint.rule_type,
                "status": latest.status,
                "margin": latest.margin,
                "margin_absolute": latest.margin_absolute,
            }
            sensitive_constraints.append(constraint_info)

            # Track tightest constraint
            if latest.margin is not None and abs(latest.margin) < abs(tightest_margin):
                tightest_margin = latest.margin
                tightest = constraint_info

    return {
        "parameter_id": parameter_id,
        "parameter_name": param.name,
        "constraints_sensitive_to_change": sensitive_constraints,
        "tightest_constraint": tightest,
    }


@router.get("/margin-report", response_model=MarginReport)
def margin_report(db: Session = Depends(get_db)):
    """Get all constraints sorted by margin (tightest first)."""
    constraints = db.query(Constraint).all()

    constraint_margins = []
    passing = 0
    failing = 0
    warnings = 0

    for constraint in constraints:
        latest = (
            db.query(EvaluationResult)
            .filter(EvaluationResult.constraint_id == constraint.id)
            .order_by(EvaluationResult.evaluated_at.desc())
            .first()
        )

        if not latest:
            latest_result = evaluate_constraint(constraint, db)
            db.add(latest_result)
            db.commit()
            latest = latest_result

        if latest.status == "pass":
            passing += 1
        elif latest.status == "fail":
            failing += 1
        else:
            warnings += 1

        margin = ConstraintMargin(
            constraint_id=constraint.id,
            constraint_name=constraint.name,
            rule_type=constraint.rule_type,
            status=latest.status,
            margin_percentage=latest.margin,
            margin_absolute=latest.margin_absolute,
            actual_value=latest.actual_value,
            limit_value=latest.limit_value,
        )
        constraint_margins.append(margin)

    # Sort by margin (tightest first, handle None values)
    def margin_sort_key(c):
        if c.margin_percentage is None:
            return float("inf")
        return abs(c.margin_percentage)

    constraint_margins.sort(key=margin_sort_key)

    return {
        "total_constraints": len(constraints),
        "passing_constraints": passing,
        "failing_constraints": failing,
        "warning_constraints": warnings,
        "constraints_by_margin": constraint_margins,
    }


@router.get("/health", response_model=SystemHealthResponse)
def system_health(db: Session = Depends(get_db)):
    """Get system-wide constraint health summary."""
    items = db.query(Item).count()
    parameters = db.query(Parameter).count()
    constraints = db.query(Constraint).count()
    from app.models.models import Trace

    traces = db.query(Trace).count()

    # Evaluate all constraints if not already done
    results = db.query(EvaluationResult).all()
    if not results:
        results = evaluate_all_constraints(db)

    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    warnings = sum(1 for r in results if r.status == "warning")

    health_pct = (passed / len(results) * 100) if results else 0

    critical_issues = []
    for result in results:
        if result.status == "fail":
            constraint = db.query(Constraint).filter(
                Constraint.id == result.constraint_id
            ).first()
            if constraint and constraint.severity == "critical":
                critical_issues.append(
                    {
                        "constraint_id": constraint.id,
                        "constraint_name": constraint.name,
                        "message": result.message,
                    }
                )

    return {
        "total_items": items,
        "total_parameters": parameters,
        "total_constraints": constraints,
        "total_traces": traces,
        "passing_constraints": passed,
        "failing_constraints": failed,
        "warning_constraints": warnings,
        "health_percentage": health_pct,
        "critical_issues": critical_issues,
    }
