/**
 * Natural language explanation layer for constraints and parameters.
 * Translates formal constraint data into human-readable explanations.
 */

import { Constraint, EvaluationResult, Item, Parameter } from "./types";
import { getRuleSymbol, formatNumber } from "./utils";

/** Generate a plain English explanation of what a constraint means */
export function explainConstraint(
  constraint: Constraint,
  sourceParam?: Parameter,
  targetParam?: Parameter,
  sourceItem?: Item,
  targetItem?: Item
): string {
  const rule = constraint.rule_type;
  const srcName = sourceParam?.name ?? "source";
  const tgtName = targetParam?.name ?? "target";
  const srcItem = sourceItem?.name ?? "";
  const tgtItem = targetItem?.name ?? "";

  switch (rule) {
    case "eq":
      return `${srcName}${srcItem ? ` (${srcItem})` : ""} must exactly equal ${tgtName}${tgtItem ? ` (${tgtItem})` : ""}. Any difference breaks this constraint.`;
    case "lte":
      return `${srcName}${srcItem ? ` (${srcItem})` : ""} must not exceed ${tgtName}${tgtItem ? ` (${tgtItem})` : ""}. Going over this limit is a violation.`;
    case "gte":
      return `${srcName}${srcItem ? ` (${srcItem})` : ""} must be at least as large as ${tgtName}${tgtItem ? ` (${tgtItem})` : ""}. Falling below is a violation.`;
    case "lt":
      return `${srcName} must be strictly less than ${tgtName}.`;
    case "gt":
      return `${srcName} must be strictly greater than ${tgtName}.`;
    case "tolerance":
      return `The difference between ${srcName} and ${tgtName} must stay within the tolerance band. Exceeding the tolerance means the system is out of spec.`;
    case "sum_lte":
      return `The combined total of all contributing parameters must not exceed ${tgtName}${tgtItem ? ` (${tgtItem})` : ""}.`;
    case "sum_gte":
      return `The combined total must be at least ${tgtName}.`;
    case "range":
      return `${srcName} must stay within the defined operating range.`;
    case "ratio_lte":
      return `The ratio of ${srcName} to ${tgtName} must not exceed the limit.`;
    default:
      return constraint.description ?? "";
  }
}

/** Generate a human-readable evaluation summary */
export function explainEvaluation(
  constraint: Constraint,
  evaluation: EvaluationResult | undefined,
  sourceParam?: Parameter,
  targetParam?: Parameter
): string {
  if (!evaluation) return "Not yet evaluated.";

  const status = evaluation.status;
  const margin = evaluation.margin;
  const actual = evaluation.actual_value;
  const limit = evaluation.limit_value;

  if (status === "unknown") return evaluation.message ?? "Unable to evaluate this constraint.";

  const rule = constraint.rule_type;
  const unit = sourceParam?.unit ?? targetParam?.unit ?? "";

  if (status === "pass") {
    if (rule === "eq") {
      return `Passing — values match exactly at ${formatNumber(actual ?? 0)} ${unit}.`;
    }
    if (margin !== null && margin !== undefined) {
      if (margin > 30) {
        return `Passing with comfortable margin (${formatNumber(margin, 1)}%). This constraint has plenty of headroom.`;
      } else if (margin > 10) {
        return `Passing with moderate margin (${formatNumber(margin, 1)}%). Worth monitoring as the design evolves.`;
      } else {
        return `Passing but tight — only ${formatNumber(margin, 1)}% margin remaining. Small changes could break this constraint.`;
      }
    }
    return `Passing. ${evaluation.message ?? ""}`;
  }

  if (status === "fail") {
    if (rule === "eq") {
      const diff = actual !== null && limit !== null ? Math.abs(actual - limit) : null;
      return `Failing — values don't match. ${actual !== null ? `Actual: ${formatNumber(actual)}` : ""}${limit !== null ? `, Required: ${formatNumber(limit)}` : ""}${diff !== null ? `. Off by ${formatNumber(diff)} ${unit}.` : "."}`;
    }
    if (rule === "lte" || rule === "sum_lte") {
      const excess = actual !== null && limit !== null ? actual - limit : null;
      return `Failing — exceeds limit by ${excess !== null ? `${formatNumber(excess)} ${unit}` : "an unknown amount"}. ${actual !== null ? `Currently at ${formatNumber(actual)}` : ""}${limit !== null ? `, limit is ${formatNumber(limit)}` : ""}.`;
    }
    if (rule === "gte") {
      const deficit = actual !== null && limit !== null ? limit - actual : null;
      return `Failing — falls short by ${deficit !== null ? `${formatNumber(deficit)} ${unit}` : "an unknown amount"}. ${actual !== null ? `Currently at ${formatNumber(actual)}` : ""}${limit !== null ? `, needs at least ${formatNumber(limit)}` : ""}.`;
    }
    if (rule === "tolerance") {
      return `Failing — the difference (${actual !== null ? formatNumber(actual) : "?"}) exceeds the tolerance (${limit !== null ? formatNumber(limit) : "?"}). The gap is too large.`;
    }
    return `Failing. ${evaluation.message ?? ""}`;
  }

  if (status === "warning") {
    return `Warning — approaching limits. ${evaluation.message ?? "Monitor closely."}`;
  }

  return evaluation.message ?? "";
}

/** Generate a severity explanation */
export function explainSeverity(severity: string): string {
  switch (severity) {
    case "critical":
      return "Critical — system will not function if this fails. Must be resolved before operation.";
    case "error":
      return "Error — system operates in degraded mode. Should be resolved before deployment.";
    case "warning":
      return "Warning — system works but performance may be impacted. Should be monitored.";
    case "info":
      return "Informational — nice to have, not a hard requirement.";
    default:
      return severity;
  }
}

/** Generate what-if impact explanation */
export function explainWhatIfImpact(
  paramName: string,
  currentValue: number,
  proposedValue: number,
  unit: string,
  affectedCount: number,
  failingCount: number,
  passingCount: number
): string {
  const direction = proposedValue > currentValue ? "increasing" : "decreasing";
  const delta = Math.abs(proposedValue - currentValue);
  const pctChange = ((delta / currentValue) * 100).toFixed(1);

  let summary = `${direction.charAt(0).toUpperCase() + direction.slice(1)} ${paramName} by ${formatNumber(delta)} ${unit} (${pctChange}% change)`;

  if (affectedCount === 0) {
    summary += " would have no impact on any constraints.";
  } else {
    summary += ` affects ${affectedCount} constraint${affectedCount !== 1 ? "s" : ""}.`;
    if (failingCount > 0) {
      summary += ` ${failingCount} would break.`;
    }
    if (passingCount > 0) {
      summary += ` ${passingCount} would be fixed.`;
    }
    if (failingCount === 0 && passingCount === 0) {
      summary += " All would remain in their current state.";
    }
  }

  return summary;
}

/** Get a color class for constraint status transition */
export function getTransitionColor(from: string, to: string): string {
  if (from === "fail" && to === "pass") return "#00b894"; // fixed
  if (from === "pass" && to === "fail") return "#e74c3c"; // broken
  if (from === to) return "#8888a0"; // unchanged
  return "#f39c12"; // other change
}

/** Get a human-readable transition label */
export function getTransitionLabel(from: string, to: string): string {
  if (from === "fail" && to === "pass") return "Would fix";
  if (from === "pass" && to === "fail") return "Would break";
  if (from === "fail" && to === "fail") return "Still failing";
  if (from === "pass" && to === "pass") return "Still passing";
  return `${from} → ${to}`;
}

/** Format a constraint rule as a readable sentence */
export function formatRule(constraint: Constraint, sourceParam?: Parameter, targetParam?: Parameter): string {
  const symbol = getRuleSymbol(constraint.rule_type);
  const src = sourceParam ? `${sourceParam.name} (${formatNumber(sourceParam.value)} ${sourceParam.unit})` : "?";
  const tgt = targetParam ? `${targetParam.name} (${formatNumber(targetParam.value)} ${targetParam.unit})` : "?";
  return `${src} ${symbol} ${tgt}`;
}
