"""Constraint evaluation engine."""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models import (
    Constraint,
    Parameter,
    EvaluationResult,
    ConstraintSource,
)


def get_parameter_value(parameter_id: str, db: Session) -> Optional[float]:
    """Get the current value of a parameter."""
    param = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    if param:
        return param.value
    return None


def get_constraint_sources(constraint_id: str, db: Session) -> list:
    """Get all constraint sources for a constraint."""
    return (
        db.query(ConstraintSource)
        .filter(ConstraintSource.constraint_id == constraint_id)
        .all()
    )


def calculate_margin(
    actual: float, limit: float, rule_type: str
) -> Tuple[Optional[float], Optional[float]]:
    """Calculate margin percentage and absolute value.

    Args:
        actual: Actual value
        limit: Limit value
        rule_type: Type of constraint

    Returns:
        (margin_percentage, margin_absolute)
    """
    if limit == 0:
        return None, actual - limit

    if rule_type in ("lte", "sum_lte", "ratio_lte"):
        # For <=, margin is (limit - actual) / limit * 100
        margin_abs = limit - actual
        margin_pct = (margin_abs / limit * 100) if limit != 0 else None
    elif rule_type in ("gte", "sum_gte"):
        # For >=, margin is (actual - limit) / limit * 100
        margin_abs = actual - limit
        margin_pct = (margin_abs / limit * 100) if limit != 0 else None
    elif rule_type in ("lt", "gt"):
        # Similar to lte/gte
        if rule_type == "lt":
            margin_abs = limit - actual
            margin_pct = (margin_abs / limit * 100) if limit != 0 else None
        else:
            margin_abs = actual - limit
            margin_pct = (margin_abs / limit * 100) if limit != 0 else None
    else:
        return None, None

    return margin_pct, margin_abs


def evaluate_constraint(constraint: Constraint, db: Session) -> EvaluationResult:
    """Evaluate a single constraint against current parameter values.

    Args:
        constraint: Constraint to evaluate
        db: Database session

    Returns:
        EvaluationResult with evaluation outcome
    """
    result = EvaluationResult(constraint_id=constraint.id)

    try:
        if constraint.rule_type in ("lte", "gte", "eq", "lt", "gt"):
            # Binary constraint: source op target
            if not constraint.source_parameter_id or not constraint.target_parameter_id:
                result.status = "unknown"
                result.message = "Missing source or target parameter"
                return result

            source_val = get_parameter_value(constraint.source_parameter_id, db)
            target_val = get_parameter_value(constraint.target_parameter_id, db)

            if source_val is None or target_val is None:
                result.status = "unknown"
                result.message = "Source or target parameter not found"
                return result

            result.actual_value = source_val
            result.limit_value = target_val

            if constraint.rule_type == "lte":
                if source_val <= target_val:
                    result.status = "pass"
                    result.message = f"{source_val} <= {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"{source_val} > {target_val} (exceeds by {source_val - target_val})"
            elif constraint.rule_type == "gte":
                if source_val >= target_val:
                    result.status = "pass"
                    result.message = f"{source_val} >= {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"{source_val} < {target_val} (below by {target_val - source_val})"
            elif constraint.rule_type == "eq":
                if source_val == target_val:
                    result.status = "pass"
                    result.message = f"{source_val} == {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"{source_val} != {target_val} (diff: {abs(source_val - target_val)})"
            elif constraint.rule_type == "lt":
                if source_val < target_val:
                    result.status = "pass"
                    result.message = f"{source_val} < {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"{source_val} >= {target_val} (exceeds by {source_val - target_val})"
            elif constraint.rule_type == "gt":
                if source_val > target_val:
                    result.status = "pass"
                    result.message = f"{source_val} > {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"{source_val} <= {target_val} (below by {target_val - source_val})"

            margin_pct, margin_abs = calculate_margin(source_val, target_val, constraint.rule_type)
            result.margin = margin_pct
            result.margin_absolute = margin_abs

        elif constraint.rule_type in ("sum_lte", "sum_gte"):
            # Multi-source constraint
            sources = get_constraint_sources(constraint.id, db)
            source_vals = []
            for source in sources:
                val = get_parameter_value(source.parameter_id, db)
                if val is not None:
                    source_vals.append(val)

            if not source_vals:
                result.status = "unknown"
                result.message = "No source parameters found"
                return result

            total = sum(source_vals)
            result.actual_value = total

            if not constraint.target_parameter_id:
                result.status = "unknown"
                result.message = "Missing target parameter"
                return result

            target_val = get_parameter_value(constraint.target_parameter_id, db)
            if target_val is None:
                result.status = "unknown"
                result.message = "Target parameter not found"
                return result

            result.limit_value = target_val

            if constraint.rule_type == "sum_lte":
                if total <= target_val:
                    result.status = "pass"
                    result.message = f"Sum {total} <= {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"Sum {total} > {target_val} (exceeds by {total - target_val})"
            else:  # sum_gte
                if total >= target_val:
                    result.status = "pass"
                    result.message = f"Sum {total} >= {target_val}"
                else:
                    result.status = "fail"
                    result.message = f"Sum {total} < {target_val} (below by {target_val - total})"

            margin_pct, margin_abs = calculate_margin(total, target_val, constraint.rule_type)
            result.margin = margin_pct
            result.margin_absolute = margin_abs

        elif constraint.rule_type == "range":
            # Range constraint
            if not constraint.source_parameter_id:
                result.status = "unknown"
                result.message = "Missing source parameter"
                return result

            source_val = get_parameter_value(constraint.source_parameter_id, db)
            if source_val is None:
                result.status = "unknown"
                result.message = "Source parameter not found"
                return result

            result.actual_value = source_val
            result.limit_value = (
                constraint.range_max
                if constraint.range_max is not None
                else constraint.range_min
            )

            min_val = constraint.range_min if constraint.range_min is not None else float("-inf")
            max_val = constraint.range_max if constraint.range_max is not None else float("inf")

            if min_val <= source_val <= max_val:
                result.status = "pass"
                result.message = f"{min_val} <= {source_val} <= {max_val}"
            else:
                result.status = "fail"
                if source_val < min_val:
                    result.message = f"{source_val} < {min_val} (below by {min_val - source_val})"
                else:
                    result.message = f"{source_val} > {max_val} (exceeds by {source_val - max_val})"

            # Calculate margin to nearest boundary
            if constraint.range_max is not None:
                margin_to_max = constraint.range_max - source_val
                margin_pct = (margin_to_max / constraint.range_max * 100) if constraint.range_max != 0 else None
                result.margin = margin_pct
                result.margin_absolute = margin_to_max

        elif constraint.rule_type == "tolerance":
            # Tolerance constraint: |source - target| <= tolerance
            if not constraint.source_parameter_id or not constraint.target_parameter_id:
                result.status = "unknown"
                result.message = "Missing source or target parameter"
                return result

            if constraint.tolerance_value is None:
                result.status = "unknown"
                result.message = "Missing tolerance value"
                return result

            source_val = get_parameter_value(constraint.source_parameter_id, db)
            target_val = get_parameter_value(constraint.target_parameter_id, db)

            if source_val is None or target_val is None:
                result.status = "unknown"
                result.message = "Source or target parameter not found"
                return result

            diff = abs(source_val - target_val)
            result.actual_value = diff
            result.limit_value = constraint.tolerance_value

            if diff <= constraint.tolerance_value:
                result.status = "pass"
                result.message = f"|{source_val} - {target_val}| = {diff} <= {constraint.tolerance_value}"
            else:
                result.status = "fail"
                result.message = f"|{source_val} - {target_val}| = {diff} > {constraint.tolerance_value}"

            margin_pct, margin_abs = calculate_margin(
                diff, constraint.tolerance_value, "lte"
            )
            result.margin = margin_pct
            result.margin_absolute = margin_abs

        elif constraint.rule_type == "ratio_lte":
            # Ratio constraint: source / target <= ratio_limit
            if not constraint.source_parameter_id or not constraint.target_parameter_id:
                result.status = "unknown"
                result.message = "Missing source or target parameter"
                return result

            if constraint.ratio_limit is None:
                result.status = "unknown"
                result.message = "Missing ratio limit"
                return result

            source_val = get_parameter_value(constraint.source_parameter_id, db)
            target_val = get_parameter_value(constraint.target_parameter_id, db)

            if source_val is None or target_val is None:
                result.status = "unknown"
                result.message = "Source or target parameter not found"
                return result

            if target_val == 0:
                result.status = "fail"
                result.message = "Target parameter is zero (division by zero)"
                return result

            ratio = source_val / target_val
            result.actual_value = ratio
            result.limit_value = constraint.ratio_limit

            if ratio <= constraint.ratio_limit:
                result.status = "pass"
                result.message = f"{source_val} / {target_val} = {ratio:.4f} <= {constraint.ratio_limit}"
            else:
                result.status = "fail"
                result.message = f"{source_val} / {target_val} = {ratio:.4f} > {constraint.ratio_limit}"

            margin_pct, margin_abs = calculate_margin(ratio, constraint.ratio_limit, "lte")
            result.margin = margin_pct
            result.margin_absolute = margin_abs

        else:
            result.status = "unknown"
            result.message = f"Unknown rule type: {constraint.rule_type}"

    except Exception as e:
        result.status = "unknown"
        result.message = f"Error evaluating constraint: {str(e)}"

    return result


def evaluate_all_constraints(db: Session) -> list:
    """Evaluate all constraints and return results.

    Args:
        db: Database session

    Returns:
        List of EvaluationResult objects
    """
    constraints = db.query(Constraint).all()
    results = []

    for constraint in constraints:
        # Delete old results for this constraint
        db.query(EvaluationResult).filter(
            EvaluationResult.constraint_id == constraint.id
        ).delete()

        # Evaluate and save new result
        result = evaluate_constraint(constraint, db)
        db.add(result)
        results.append(result)

    db.commit()
    return results
