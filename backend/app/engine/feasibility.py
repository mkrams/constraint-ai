"""Feasibility analysis for parameters."""

from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Constraint, Parameter, ConstraintSource
from app.engine.evaluator import get_parameter_value, get_constraint_sources


def get_feasible_range(parameter_id: str, db: Session) -> Optional[Dict]:
    """Calculate the feasible range for a parameter given all constraints.

    Finds all constraints involving this parameter and calculates the valid
    range of values that would satisfy all constraints.

    Args:
        parameter_id: ID of the parameter to analyze
        db: Database session

    Returns:
        Dict with min, max, current_value, margins, or None if parameter not found
    """
    # Get the parameter
    param = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    if not param:
        return None

    current_value = param.value

    # Start with infinite bounds
    feasible_min = float("-inf")
    feasible_max = float("inf")

    # Find all constraints where this parameter appears
    constraints = db.query(Constraint).filter(
        or_(
            Constraint.source_parameter_id == parameter_id,
            Constraint.target_parameter_id == parameter_id,
        )
    ).all()

    # Also check constraint sources
    constraint_ids = [c.id for c in constraints]
    source_constraints = (
        db.query(Constraint)
        .join(
            ConstraintSource,
            Constraint.id == ConstraintSource.constraint_id,
        )
        .filter(ConstraintSource.parameter_id == parameter_id)
        .all()
    )
    constraints.extend(source_constraints)

    constraint_bounds = []

    for constraint in constraints:
        bounds = _calculate_constraint_bounds(constraint, parameter_id, db)
        if bounds:
            constraint_bounds.append(bounds)
            min_bound, max_bound = bounds
            if min_bound > feasible_min:
                feasible_min = min_bound
            if max_bound < feasible_max:
                feasible_max = max_bound

    # Handle case where no feasible range exists
    if feasible_min > feasible_max:
        return {
            "parameter_id": parameter_id,
            "parameter_name": param.name,
            "current_value": current_value,
            "min_value": None,
            "max_value": None,
            "feasible": False,
            "margin_to_min": None,
            "margin_to_max": None,
            "unit": param.unit,
            "conflicting_constraints": len(constraint_bounds),
        }

    # Calculate margins
    margin_to_min = None
    margin_to_max = None

    if feasible_min > float("-inf"):
        margin_to_min = current_value - feasible_min
    if feasible_max < float("inf"):
        margin_to_max = feasible_max - current_value

    return {
        "parameter_id": parameter_id,
        "parameter_name": param.name,
        "current_value": current_value,
        "min_value": feasible_min if feasible_min > float("-inf") else None,
        "max_value": feasible_max if feasible_max < float("inf") else None,
        "feasible": feasible_min <= current_value <= feasible_max,
        "margin_to_min": margin_to_min,
        "margin_to_max": margin_to_max,
        "unit": param.unit,
        "num_constraining_constraints": len(constraint_bounds),
    }


def _calculate_constraint_bounds(
    constraint: Constraint, parameter_id: str, db: Session
) -> Optional[Tuple[float, float]]:
    """Calculate the bounds this constraint imposes on a parameter.

    Args:
        constraint: Constraint to analyze
        parameter_id: Parameter ID to analyze
        db: Database session

    Returns:
        Tuple of (min_bound, max_bound) or None if cannot determine
    """
    try:
        if constraint.rule_type == "lte":
            # source <= target
            if constraint.source_parameter_id == parameter_id:
                # This parameter is the source, so it must be <= target
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None:
                    return (float("-inf"), target_val)
            elif constraint.target_parameter_id == parameter_id:
                # This parameter is the target, so it must be >= source
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                if source_val is not None:
                    return (source_val, float("inf"))

        elif constraint.rule_type == "gte":
            # source >= target
            if constraint.source_parameter_id == parameter_id:
                # This parameter is the source, so it must be >= target
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None:
                    return (target_val, float("inf"))
            elif constraint.target_parameter_id == parameter_id:
                # This parameter is the target, so it must be <= source
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                if source_val is not None:
                    return (float("-inf"), source_val)

        elif constraint.rule_type == "lt":
            # source < target
            if constraint.source_parameter_id == parameter_id:
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None:
                    # Slightly less than target
                    return (float("-inf"), target_val - 1e-6)
            elif constraint.target_parameter_id == parameter_id:
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                if source_val is not None:
                    return (source_val + 1e-6, float("inf"))

        elif constraint.rule_type == "gt":
            # source > target
            if constraint.source_parameter_id == parameter_id:
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None:
                    return (target_val + 1e-6, float("inf"))
            elif constraint.target_parameter_id == parameter_id:
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                if source_val is not None:
                    return (float("-inf"), source_val - 1e-6)

        elif constraint.rule_type == "range":
            if constraint.source_parameter_id == parameter_id:
                min_val = (
                    constraint.range_min
                    if constraint.range_min is not None
                    else float("-inf")
                )
                max_val = (
                    constraint.range_max
                    if constraint.range_max is not None
                    else float("inf")
                )
                return (min_val, max_val)

        elif constraint.rule_type == "tolerance":
            # |source - target| <= tolerance
            if constraint.source_parameter_id == parameter_id:
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None and constraint.tolerance_value is not None:
                    min_bound = target_val - constraint.tolerance_value
                    max_bound = target_val + constraint.tolerance_value
                    return (min_bound, max_bound)
            elif constraint.target_parameter_id == parameter_id:
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                if source_val is not None and constraint.tolerance_value is not None:
                    min_bound = source_val - constraint.tolerance_value
                    max_bound = source_val + constraint.tolerance_value
                    return (min_bound, max_bound)

        elif constraint.rule_type == "ratio_lte":
            # source / target <= ratio
            if constraint.source_parameter_id == parameter_id:
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None and constraint.ratio_limit is not None:
                    max_bound = target_val * constraint.ratio_limit
                    return (float("-inf"), max_bound)
            elif constraint.target_parameter_id == parameter_id:
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                if (
                    source_val is not None
                    and constraint.ratio_limit is not None
                    and constraint.ratio_limit != 0
                ):
                    min_bound = source_val / constraint.ratio_limit
                    return (min_bound, float("inf"))

        elif constraint.rule_type == "sum_lte":
            # sum(sources) <= target
            sources = get_constraint_sources(constraint.id, db)
            if any(s.parameter_id == parameter_id for s in sources):
                # This parameter is one of the sources
                target_val = get_parameter_value(constraint.target_parameter_id, db)
                if target_val is not None:
                    # Sum of other sources
                    other_sum = 0
                    for source in sources:
                        if source.parameter_id != parameter_id:
                            val = get_parameter_value(source.parameter_id, db)
                            if val is not None:
                                other_sum += val
                    # This param must be <= (target - other_sum)
                    return (float("-inf"), target_val - other_sum)

            elif constraint.target_parameter_id == parameter_id:
                # This is the target, sum of sources must be <= target
                sources = get_constraint_sources(constraint.id, db)
                source_sum = 0
                for source in sources:
                    val = get_parameter_value(source.parameter_id, db)
                    if val is not None:
                        source_sum += val
                # Target must be >= source_sum
                return (source_sum, float("inf"))

    except Exception:
        return None

    return None
