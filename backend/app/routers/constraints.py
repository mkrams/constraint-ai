"""API router for constraints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Constraint, ConstraintSource, Parameter, EvaluationResult
from app.models.schemas import (
    ConstraintCreate,
    ConstraintUpdate,
    ConstraintResponse,
    ConstraintDetailResponse,
    EvaluationResultResponse,
)
from app.engine.evaluator import evaluate_constraint, evaluate_all_constraints

router = APIRouter(prefix="/api/constraints", tags=["constraints"])


@router.get("/", response_model=List[ConstraintDetailResponse])
def list_constraints(db: Session = Depends(get_db)):
    """List all constraints with their latest evaluation results."""
    constraints = db.query(Constraint).all()
    results = []

    for constraint in constraints:
        # Get latest evaluation result
        latest_result = (
            db.query(EvaluationResult)
            .filter(EvaluationResult.constraint_id == constraint.id)
            .order_by(EvaluationResult.evaluated_at.desc())
            .first()
        )

        constraint_dict = {
            "id": constraint.id,
            "name": constraint.name,
            "description": constraint.description,
            "rule_type": constraint.rule_type,
            "severity": constraint.severity,
            "expression": constraint.expression,
            "source_parameter_id": constraint.source_parameter_id,
            "target_parameter_id": constraint.target_parameter_id,
            "range_min": constraint.range_min,
            "range_max": constraint.range_max,
            "tolerance_value": constraint.tolerance_value,
            "ratio_limit": constraint.ratio_limit,
            "domain_descriptions": constraint.domain_descriptions,
            "ai_explanation": constraint.ai_explanation,
            "created_at": constraint.created_at,
            "updated_at": constraint.updated_at,
            "sources": constraint.sources,
            "latest_result": latest_result,
        }
        results.append(constraint_dict)

    return results


@router.post("/", response_model=ConstraintResponse, status_code=status.HTTP_201_CREATED)
def create_constraint(constraint: ConstraintCreate, db: Session = Depends(get_db)):
    """Create a new constraint."""
    # Validate that referenced parameters exist
    if constraint.source_parameter_id:
        param = db.query(Parameter).filter(Parameter.id == constraint.source_parameter_id).first()
        if not param:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source parameter not found",
            )

    if constraint.target_parameter_id:
        param = db.query(Parameter).filter(Parameter.id == constraint.target_parameter_id).first()
        if not param:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target parameter not found",
            )

    db_constraint = Constraint(
        name=constraint.name,
        description=constraint.description,
        rule_type=constraint.rule_type,
        severity=constraint.severity,
        expression=constraint.expression,
        source_parameter_id=constraint.source_parameter_id,
        target_parameter_id=constraint.target_parameter_id,
        range_min=constraint.range_min,
        range_max=constraint.range_max,
        tolerance_value=constraint.tolerance_value,
        ratio_limit=constraint.ratio_limit,
        domain_descriptions=constraint.domain_descriptions or {},
    )

    db.add(db_constraint)
    db.flush()

    # Add constraint sources
    if constraint.sources:
        for source in constraint.sources:
            param = db.query(Parameter).filter(Parameter.id == source.parameter_id).first()
            if not param:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parameter {source.parameter_id} not found",
                )
            db_source = ConstraintSource(
                constraint_id=db_constraint.id,
                parameter_id=source.parameter_id,
                role=source.role,
            )
            db.add(db_source)

    db.commit()
    db.refresh(db_constraint)
    return db_constraint


@router.get("/{constraint_id}", response_model=ConstraintDetailResponse)
def get_constraint(constraint_id: str, db: Session = Depends(get_db)):
    """Get a specific constraint with full details."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found"
        )

    # Get latest evaluation result
    latest_result = (
        db.query(EvaluationResult)
        .filter(EvaluationResult.constraint_id == constraint.id)
        .order_by(EvaluationResult.evaluated_at.desc())
        .first()
    )

    constraint_dict = {
        "id": constraint.id,
        "name": constraint.name,
        "description": constraint.description,
        "rule_type": constraint.rule_type,
        "severity": constraint.severity,
        "expression": constraint.expression,
        "source_parameter_id": constraint.source_parameter_id,
        "target_parameter_id": constraint.target_parameter_id,
        "range_min": constraint.range_min,
        "range_max": constraint.range_max,
        "tolerance_value": constraint.tolerance_value,
        "ratio_limit": constraint.ratio_limit,
        "domain_descriptions": constraint.domain_descriptions,
        "ai_explanation": constraint.ai_explanation,
        "created_at": constraint.created_at,
        "updated_at": constraint.updated_at,
        "sources": constraint.sources,
        "latest_result": latest_result,
    }

    return constraint_dict


@router.put("/{constraint_id}", response_model=ConstraintResponse)
def update_constraint(
    constraint_id: str, constraint_update: ConstraintUpdate, db: Session = Depends(get_db)
):
    """Update a constraint."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found"
        )

    update_data = constraint_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(constraint, field, value)

    db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return constraint


@router.delete("/{constraint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_constraint(constraint_id: str, db: Session = Depends(get_db)):
    """Delete a constraint and its related records."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found"
        )

    # Delete related evaluation results first
    db.query(EvaluationResult).filter(
        EvaluationResult.constraint_id == constraint_id
    ).delete()

    # Delete related constraint sources
    db.query(ConstraintSource).filter(
        ConstraintSource.constraint_id == constraint_id
    ).delete()

    db.delete(constraint)
    db.commit()


@router.post("/{constraint_id}/evaluate", response_model=EvaluationResultResponse)
def evaluate_single_constraint(
    constraint_id: str, db: Session = Depends(get_db)
):
    """Evaluate a single constraint."""
    constraint = db.query(Constraint).filter(Constraint.id == constraint_id).first()
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Constraint not found"
        )

    # Delete old results
    db.query(EvaluationResult).filter(
        EvaluationResult.constraint_id == constraint.id
    ).delete()

    # Evaluate and save
    result = evaluate_constraint(constraint, db)
    db.add(result)
    db.commit()
    db.refresh(result)

    return result


@router.post("/evaluate-all", response_model=dict)
def evaluate_all(db: Session = Depends(get_db)):
    """Evaluate all constraints and return summary."""
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
        "results": [
            {
                "id": r.id,
                "constraint_id": r.constraint_id,
                "status": r.status,
                "actual_value": r.actual_value,
                "limit_value": r.limit_value,
                "margin": r.margin,
                "margin_absolute": r.margin_absolute,
                "message": r.message,
                "evaluated_at": r.evaluated_at,
            }
            for r in results
        ],
    }
