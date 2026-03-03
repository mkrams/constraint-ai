import {
  Item,
  Constraint,
  Trace,
  EvaluationResponse,
  WhatIfResponse,
  HealthResponse,
  MarginReport,
  FeasibilityResponse,
  Parameter,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Items
  getItems: async (): Promise<Item[]> => {
    return fetchAPI<Item[]>("/api/items/");
  },

  // Traces
  getTraces: async (): Promise<Trace[]> => {
    return fetchAPI<Trace[]>("/api/traces/");
  },

  // Constraints
  getConstraints: async (): Promise<Constraint[]> => {
    return fetchAPI<Constraint[]>("/api/constraints/");
  },

  createConstraint: async (constraint: Partial<Constraint>) => {
    return fetchAPI("/api/constraints/", {
      method: "POST",
      body: JSON.stringify(constraint),
    });
  },

  // Engine - Evaluation
  evaluateAll: async (): Promise<EvaluationResponse> => {
    return fetchAPI<EvaluationResponse>("/api/engine/evaluate-all", {
      method: "POST",
    });
  },

  // Engine - What-If
  whatIf: async (
    parameterId: string,
    proposedValue: number
  ): Promise<WhatIfResponse> => {
    return fetchAPI<WhatIfResponse>("/api/engine/what-if", {
      method: "POST",
      body: JSON.stringify({
        parameter_id: parameterId,
        proposed_value: proposedValue,
      }),
    });
  },

  // Engine - Health
  getHealth: async (): Promise<HealthResponse> => {
    return fetchAPI<HealthResponse>("/api/engine/health");
  },

  // Engine - Margin Report
  getMarginReport: async (): Promise<MarginReport> => {
    return fetchAPI<MarginReport>("/api/engine/margin-report");
  },

  // Engine - Feasibility
  getFeasibility: async (parameterId: string): Promise<FeasibilityResponse> => {
    return fetchAPI<FeasibilityResponse>(
      `/api/engine/feasibility/${parameterId}`,
      {
        method: "POST",
      }
    );
  },

  // Parameters
  updateParameter: async (parameterId: string, value: number) => {
    return fetchAPI(`/api/parameters/${parameterId}/value`, {
      method: "PUT",
      body: JSON.stringify({ value }),
    });
  },
};
