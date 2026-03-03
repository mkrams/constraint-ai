import { Constraint, EvaluationResult, Parameter } from "./types";

export function getDomainColor(domain: string): string {
  const colors: Record<string, string> = {
    electrical: "#6c5ce7",
    thermal: "#e74c3c",
    mechanical: "#00b894",
    systems: "#f39c12",
    software: "#3498db",
    default: "#8888a0",
  };
  return colors[domain.toLowerCase()] || colors.default;
}

export function getStatusColor(status: "pass" | "fail" | "warning" | "unknown"): string {
  switch (status) {
    case "pass":
      return "#00b894";
    case "fail":
      return "#e74c3c";
    case "warning":
      return "#f39c12";
    default:
      return "#8888a0";
  }
}

export function getRuleSymbol(ruleType: string): string {
  const symbols: Record<string, string> = {
    lte: "≤",
    gte: "≥",
    eq: "=",
    lt: "<",
    gt: ">",
    neq: "≠",
  };
  return symbols[ruleType] || ruleType;
}

export function formatNumber(value: number, decimals: number = 2): string {
  if (typeof value !== "number") return "N/A";
  return value.toFixed(decimals);
}

export function getConstraintLabel(
  constraint: Constraint,
  sourceParam: Parameter | undefined,
  targetParam: Parameter | undefined
): string {
  if (!sourceParam || !targetParam) return constraint.name;
  return `${sourceParam.value} ${getRuleSymbol(constraint.rule_type)} ${targetParam.value}`;
}

export function calculateMarginPercentage(result: EvaluationResult): number {
  if (!result.limit_value || !result.margin) return 0;
  return Math.min(100, Math.max(0, (result.margin / 100) * 100));
}
