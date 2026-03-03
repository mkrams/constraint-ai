"""Impact analysis and constraint propagation."""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Constraint, Parameter, ConstraintSource, Item
from app.engine.evaluator import evaluate_constraint, get_parameter_value


def analyze_change_impact(
    parameter_id: str, proposed_value: float, db: Session
) -> Dict[str, Any]:
    """Analyze the impact of changing a parameter value.

    Does not modify the database. Evaluates how constraints would be affected
    if the parameter were changed to the proposed value.

    Args:
        parameter_id: ID of parameter to change
        proposed_value: Proposed new value
        db: Database session

    Returns:
        Impact analysis dict with affected constraints and recommendations
    """
    param = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    if not param:
        return {"error": "Parameter not found"}

    current_value = param.value
    item = db.query(Item).filter(Item.id == param.item_id).first()

    # Find all constraints involving this parameter
    constraints = db.query(Constraint).filter(
        or_(
            Constraint.source_parameter_id == parameter_id,
            Constraint.target_parameter_id == parameter_id,
        )
    ).all()

    # Also check constraint sources
    constraint_ids_with_sources = (
        db.query(Constraint.id)
        .join(
            ConstraintSource,
            Constraint.id == ConstraintSource.constraint_id,
        )
        .filter(ConstraintSource.parameter_id == parameter_id)
        .all()
    )
    constraint_ids_with_sources = [c[0] for c in constraint_ids_with_sources]
    for cid in constraint_ids_with_sources:
        c = db.query(Constraint).filter(Constraint.id == cid).first()
        if c and c not in constraints:
            constraints.append(c)

    affected_constraints = []
    newly_failing = []
    newly_passing = []

    for constraint in constraints:
        # Get current status
        current_result = db.query(Constraint.__table__.c).filter(
            Constraint.id == constraint.id
        ).first()

        # Create a temporary copy to evaluate with proposed value
        temp_result = _evaluate_with_proposed_value(
            constraint, parameter_id, proposed_value, db
        )

        affected = {
            "constraint_id": constraint.id,
            "constraint_name": constraint.name,
            "rule_type": constraint.rule_type,
            "current_status": "unknown",
            "proposed_status": temp_result["status"],
            "message": temp_result["message"],
            "margin": temp_result.get("margin"),
            "margin_absolute": temp_result.get("margin_absolute"),
        }

        # Get current status from database
        from app.models.models import EvaluationResult

        current_eval = (
            db.query(EvaluationResult)
            .filter(EvaluationResult.constraint_id == constraint.id)
            .order_by(EvaluationResult.evaluated_at.desc())
            .first()
        )
        if current_eval:
            affected["current_status"] = current_eval.status

        affected_constraints.append(affected)

        if current_eval and current_eval.status != "fail" and temp_result["status"] == "fail":
            newly_failing.append(affected)
        elif (
            current_eval
            and current_eval.status == "fail"
            and temp_result["status"] != "fail"
        ):
            newly_passing.append(affected)

    feasible = len(newly_failing) == 0
    summary = f"Changing {param.name} from {current_value} to {proposed_value} "
    if feasible:
        summary += f"would keep all constraints valid."
        if newly_passing:
            summary += f" Would fix {len(newly_passing)} constraint(s)."
    else:
        summary += f"would break {len(newly_failing)} constraint(s)."

    return {
        "parameter_id": parameter_id,
        "parameter_name": param.name,
        "item_id": param.item_id,
        "item_name": item.name if item else None,
        "current_value": current_value,
        "proposed_value": proposed_value,
        "feasible": feasible,
        "summary": summary,
        "affected_constraints": affected_constraints,
        "newly_failing": newly_failing,
        "newly_passing": newly_passing,
        "total_affected": len(affected_constraints),
    }


def analyze_full_impact(
    parameter_id: str, proposed_value: float, db: Session
) -> Dict[str, Any]:
    """Perform comprehensive downstream impact analysis.

    Analyzes not just the direct impact, but also cascading effects
    on other parameters that might need to change.

    Args:
        parameter_id: ID of parameter to change
        proposed_value: Proposed new value
        db: Database session

    Returns:
        Comprehensive impact analysis with cascading effects
    """
    primary_impact = analyze_change_impact(parameter_id, proposed_value, db)

    if "error" in primary_impact:
        return primary_impact

    # For each newly failing constraint, try to identify what other
    # parameters would need to change to fix it
    cascading_impacts = []

    for failing_constraint in primary_impact.get("newly_failing", []):
        constraint = db.query(Constraint).filter(
            Constraint.id == failing_constraint["constraint_id"]
        ).first()
        if not constraint:
            continue

        # Identify the "other" parameter in this constraint
        other_param_id = None
        if constraint.source_parameter_id == parameter_id:
            other_param_id = constraint.target_parameter_id
        elif constraint.target_parameter_id == parameter_id:
            other_param_id = constraint.source_parameter_id

        if other_param_id:
            other_param = db.query(Parameter).filter(
                Parameter.id == other_param_id
            ).first()
            if other_param:
                # Calculate what the other parameter would need to be
                required_value = _calculate_required_value(
                    constraint, parameter_id, proposed_value, db
                )
                if required_value is not None:
                    cascading_impacts.append(
                        {
                            "parameter_id": other_param_id,
                            "parameter_name": other_param.name,
                            "current_value": other_param.value,
                            "required_value": required_value,
                            "to_satisfy_constraint": failing_constraint[
                                "constraint_name"
                            ],
                        }
                    )

    return {
        "primary_parameter": primary_impact,
        "cascading_impacts": cascading_impacts,
        "feasible_without_changes": len(primary_impact.get("newly_failing", [])) == 0,
        "feasible_with_changes": (
            len(primary_impact.get("newly_failing", [])) <= len(cascading_impacts)
        ),
    }


def _evaluate_with_proposed_value(
    constraint: Constraint, parameter_id: str, proposed_value: float, db: Session
) -> Dict[str, Any]:
    """Evaluate a constraint as if a parameter had a proposed value.

    Args:
        constraint: Constraint to evaluate
        parameter_id: Parameter being changed
        proposed_value: Proposed new value
        db: Database session

    Returns:
        Evaluation result dict
    """
    from app.engine.evaluator import get_constraint_sources, calculate_margin

    try:
        if constraint.rule_type in ("lte", "gte", "eq", "lt", "gt"):
            if constraint.source_parameter_id == parameter_id:
                source_val = proposed_value
                target_val = get_parameter_value(constraint.target_parameter_id, db)
            elif constraint.target_parameter_id == parameter_id:
                source_val = get_parameter_value(constraint.source_parameter_id, db)
                target_val = proposed_value
            else:
                return {"status": "unknown", "message": "Parameter not in constraint"}

            if source_val is None or target_val is None:
                return {"status": "unknown", "message": "Missing parameter values"}

            if constraint.rule_type == "lte":
                status = "pass" if source_val <= target_val else "fail"
            elif constraint.rule_type == "gte":
                status = "pass" if source_val >= target_val else "fail"
            elif constraint.rule_type == "eq":
                status = "pass" if source_val == target_val else "fail"
            elif constraint.rule_type == "lt":
                status = "pass" if source_val < target_val else "fail"
            else:  # gt
                status = "pass" if source_val > target_val else "fail"

            margin_pct, margin_abs = calculate_margin(source_val, target_val, constraint.rule_type)
            return {
                "status": status,
                "actual_value": source_val,
                "limit_value": target_val,
                "margin": margin_pct,
                "margin_absolute": margin_abs,
                "message": f"{source_val} {constraint.rule_type} {target_val}",
            }

        elif constraint.rule_type == "range":
            if constraint.source_parameter_id == parameter_id:
                source_val = proposed_value
            else:
                return {"status": "unknown", "message": "Parameter not in constraint"}

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

            status = "pass" if min_val <= source_val <= max_val else "fail"
            return {
                "status": status,
                "actual_value": source_val,
                "limit_value": max_val if max_val != float("inf") else min_val,
                "message": f"{min_val} <= {source_val} <= {max_val}",
            }

        elif constraint.rule_type == "sum_lte":
            sources = get_constraint_sources(constraint.id, db)
            total = 0
            for source in sources:
                if source.parameter_id == parameter_id:
                    total += proposed_value
                else:
                    val = get_parameter_value(source.parameter_id, db)
                    if val is not None:
                        total += val

            target_val = get_parameter_value(constraint.target_parameter_id, db)
            if target_val is None:
                return {"status": "unknown", "message": "Target not found"}

            status = "pass" if total <= target_val else "fail"
            margin_pct, margin_abs = calculate_margin(total, target_val, "sum_lte")
            return {
                "status": status,
                "actual_value": total,
                "limit_value": target_val,
                "margin": margin_pct,
                "margin_absolute": margin_abs,
                "message": f"Sum {total} {'<=' if status == 'pass' else '>'} {target_val}",
            }

        else:
            return {"status": "unknown", "message": f"Unsupported rule type: {constraint.rule_type}"}

    except Exception as e:
        return {"status": "unknown", "message": f"Error: {str(e)}"}


def _calculate_required_value(
    constraint: Constraint, changed_param_id: str, changed_value: float, db: Session
) -> Optional[float]:
    """Calculate what value another parameter needs to satisfy a constraint.

    Args:
        constraint: Constraint that needs to be satisfied
        changed_param_id: Parameter being changed
        changed_value: New value of changed parameter
        db: Database session

    Returns:
        Required value for the other parameter, or None if cannot calculate
    """
    try:
        if constraint.rule_type == "lte":
            if constraint.source_parameter_id == changed_param_id:
                # changed_value <= target, so target >= changed_value
                return changed_value
            else:
                # source <= changed_value, so source <= changed_value
                return changed_value

        elif constraint.rule_type == "gte":
            if constraint.source_parameter_id == changed_param_id:
                # changed_value >= target, so target <= changed_value
                return changed_value
            else:
                # source >= changed_value, so source >= changed_value
                return changed_value

        elif constraint.rule_type == "sum_lte":
            if constraint.target_parameter_id == changed_param_id:
                # sum <= target, target >= sum
                sources = get_constraint_sources(constraint.id, db)
                other_sum = 0
                for source in sources:
                    if source.parameter_id != changed_param_id:
                        val = get_parameter_value(source.parameter_id, db)
                        if val is not None:
                            other_sum += val
                return other_sum

    except Exception:
        return None

    return None
