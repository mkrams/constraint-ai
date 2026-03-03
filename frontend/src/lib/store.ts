import { create } from "zustand";
import {
  Item,
  Parameter,
  Trace,
  Constraint,
  EvaluationResult,
  WhatIfConstraint,
} from "./types";

interface AppStore {
  // Data
  items: Item[];
  parameters: Parameter[];
  traces: Trace[];
  constraints: Constraint[];
  evaluationResults: EvaluationResult[];

  // UI State
  selectedNodeId: string | null;
  selectedConstraintId: string | null;
  selectedParameterId: string | null;
  domainFilter: string | null;
  loading: boolean;
  error: string | null;

  // What-If Mode
  whatIfMode: boolean;
  whatIfParameterId: string | null;
  whatIfValue: number | null;
  whatIfResults: WhatIfConstraint[] | null;

  // Health
  healthStatus: {
    passed: number;
    failed: number;
    warnings: number;
    total: number;
  } | null;

  // Actions
  setItems: (items: Item[]) => void;
  setParameters: (parameters: Parameter[]) => void;
  setTraces: (traces: Trace[]) => void;
  setConstraints: (constraints: Constraint[]) => void;
  setEvaluationResults: (results: EvaluationResult[]) => void;
  setSelectedNodeId: (id: string | null) => void;
  setSelectedConstraintId: (id: string | null) => void;
  setSelectedParameterId: (id: string | null) => void;
  setDomainFilter: (domain: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // What-If Actions
  setWhatIfMode: (enabled: boolean) => void;
  setWhatIfParameter: (parameterId: string | null, value: number | null) => void;
  setWhatIfResults: (results: WhatIfConstraint[] | null) => void;
  clearWhatIf: () => void;

  // Health Actions
  setHealthStatus: (status: {
    passed: number;
    failed: number;
    warnings: number;
    total: number;
  } | null) => void;

  // Helper Methods
  getItemById: (id: string) => Item | undefined;
  getConstraintById: (id: string) => Constraint | undefined;
  getParameterById: (id: string) => Parameter | undefined;
  getItemByParameterId: (parameterId: string) => Item | undefined;
  getConstraintsForItem: (itemId: string) => Constraint[];
  getEvaluationForConstraint: (
    constraintId: string
  ) => EvaluationResult | undefined;
  getParametersForItem: (itemId: string) => Parameter[];
  getFilteredItems: () => Item[];
}

export const useStore = create<AppStore>((set, get) => ({
  // Initial State
  items: [],
  parameters: [],
  traces: [],
  constraints: [],
  evaluationResults: [],
  selectedNodeId: null,
  selectedConstraintId: null,
  selectedParameterId: null,
  domainFilter: null,
  loading: false,
  error: null,
  whatIfMode: false,
  whatIfParameterId: null,
  whatIfValue: null,
  whatIfResults: null,
  healthStatus: null,

  // Actions
  setItems: (items) => set({ items }),
  setParameters: (parameters) => set({ parameters }),
  setTraces: (traces) => set({ traces }),
  setConstraints: (constraints) => set({ constraints }),
  setEvaluationResults: (results) => set({ evaluationResults: results }),
  setSelectedNodeId: (id) =>
    set({ selectedNodeId: id, selectedConstraintId: null }),
  setSelectedConstraintId: (id) =>
    set({ selectedConstraintId: id, selectedNodeId: null }),
  setSelectedParameterId: (id) => set({ selectedParameterId: id }),
  setDomainFilter: (domain) => set({ domainFilter: domain }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  setWhatIfMode: (enabled) => {
    if (!enabled) {
      set({
        whatIfMode: false,
        whatIfParameterId: null,
        whatIfValue: null,
        whatIfResults: null,
      });
    } else {
      set({ whatIfMode: true });
    }
  },
  setWhatIfParameter: (parameterId, value) =>
    set({ whatIfParameterId: parameterId, whatIfValue: value }),
  setWhatIfResults: (results) => set({ whatIfResults: results }),
  clearWhatIf: () =>
    set({
      whatIfMode: false,
      whatIfParameterId: null,
      whatIfValue: null,
      whatIfResults: null,
    }),

  setHealthStatus: (status) => set({ healthStatus: status }),

  // Helper Methods
  getItemById: (id) => {
    const state = get();
    return state.items.find((item) => item.id === id);
  },

  getConstraintById: (id) => {
    const state = get();
    return state.constraints.find((c) => c.id === id);
  },

  getParameterById: (id) => {
    const state = get();
    return state.parameters.find((p) => p.id === id);
  },

  getItemByParameterId: (parameterId) => {
    const state = get();
    return state.items.find((item) =>
      item.parameters.some((p) => p.id === parameterId)
    );
  },

  getConstraintsForItem: (itemId) => {
    const state = get();
    const itemParams = state.items
      .find((item) => item.id === itemId)
      ?.parameters.map((p) => p.id) || [];

    return state.constraints.filter(
      (c) =>
        itemParams.includes(c.source_parameter_id) ||
        itemParams.includes(c.target_parameter_id)
    );
  },

  getEvaluationForConstraint: (constraintId) => {
    const state = get();
    return state.evaluationResults.find((r) => r.constraint_id === constraintId);
  },

  getParametersForItem: (itemId) => {
    const state = get();
    const item = state.items.find((i) => i.id === itemId);
    return item?.parameters || [];
  },

  getFilteredItems: () => {
    const state = get();
    if (!state.domainFilter) {
      return state.items;
    }
    return state.items.filter((item) => item.domain === state.domainFilter);
  },
}));
