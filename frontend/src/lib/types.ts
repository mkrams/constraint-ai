// API Response Types
export interface Parameter {
  id: string;
  item_id: string;
  name: string;
  value: number;
  unit: string;
  param_type: string;
}

export interface Item {
  id: string;
  short_id: string;
  name: string;
  item_type: string;
  domain: string;
  parameters: Parameter[];
}

export interface Constraint {
  id: string;
  name: string;
  description: string;
  rule_type: string;
  severity: string;
  source_parameter_id: string;
  target_parameter_id: string;
  domain_descriptions?: Record<string, string>;
}

export interface Trace {
  id: string;
  source_item_id: string;
  target_item_id: string;
  trace_type: string;
  description: string;
}

export interface EvaluationResult {
  constraint_id: string;
  status: "pass" | "fail" | "warning" | "unknown";
  actual_value: number;
  limit_value: number;
  margin: number;
  margin_absolute: number;
  message: string;
}

export interface EvaluationResponse {
  total_constraints: number;
  passed: number;
  failed: number;
  warnings: number;
  results: EvaluationResult[];
}

export interface WhatIfResponse {
  parameter_id: string;
  proposed_value: number;
  current_value: number;
  directly_affected_constraints: EvaluationResult[];
  newly_failing: EvaluationResult[];
  newly_passing: EvaluationResult[];
  summary: {
    total_affected: number;
    would_fail: number;
    would_pass: number;
  };
}

export interface HealthResponse {
  status: string;
  total_constraints: number;
  passed: number;
  failed: number;
  warnings: number;
  last_evaluated: string;
}

export interface MarginReport {
  constraints: Array<EvaluationResult & { constraint: Constraint }>;
}

export interface FeasibilityResponse {
  parameter_id: string;
  min_value: number;
  max_value: number;
  current_value: number;
  feasible: boolean;
}
