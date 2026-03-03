"use client";

import { Item, Constraint, EvaluationResult, Parameter } from "@/lib/types";
import { useStore } from "@/lib/store";
import { ConstraintDetail } from "./ConstraintDetail";
import { ItemDetail } from "./ItemDetail";
import { WhatIfPanel } from "./WhatIfPanel";

interface RightPanelProps {
  items: Item[];
  constraints: Constraint[];
  evaluationResults: EvaluationResult[];
  parameters: Parameter[];
}

export function RightPanel({
  items,
  constraints,
  evaluationResults,
  parameters,
}: RightPanelProps) {
  const selectedNodeId = useStore((s) => s.selectedNodeId);
  const selectedConstraintId = useStore((s) => s.selectedConstraintId);
  const whatIfMode = useStore((s) => s.whatIfMode);

  const selectedItem = items.find((i) => i.id === selectedNodeId);
  const selectedConstraint = constraints.find(
    (c) => c.id === selectedConstraintId
  );

  if (whatIfMode) {
    return (
      <div className="panel-content">
        <WhatIfPanel parameters={parameters} evaluationResults={evaluationResults} />
      </div>
    );
  }

  if (selectedConstraint) {
    const sourceParam = parameters.find(
      (p) => p.id === selectedConstraint.source_parameter_id
    );
    const targetParam = parameters.find(
      (p) => p.id === selectedConstraint.target_parameter_id
    );
    const sourceItem = items.find((i) =>
      i.parameters.some((p) => p.id === selectedConstraint.source_parameter_id)
    );
    const targetItem = items.find((i) =>
      i.parameters.some((p) => p.id === selectedConstraint.target_parameter_id)
    );
    const evaluation = evaluationResults.find(
      (r) => r.constraint_id === selectedConstraint.id
    );

    return (
      <div className="panel-content">
        <ConstraintDetail
          constraint={selectedConstraint}
          evaluation={evaluation}
          sourceParam={sourceParam}
          targetParam={targetParam}
          sourceItem={sourceItem}
          targetItem={targetItem}
        />
      </div>
    );
  }

  if (selectedItem) {
    const itemConstraints = constraints.filter(
      (c) =>
        selectedItem.parameters.some((p) => p.id === c.source_parameter_id) ||
        selectedItem.parameters.some((p) => p.id === c.target_parameter_id)
    );

    return (
      <div className="panel-content">
        <ItemDetail
          item={selectedItem}
          constraints={itemConstraints}
          evaluationResults={evaluationResults}
        />
      </div>
    );
  }

  return (
    <div className="panel-content text-center py-8">
      <p className="text-[#8888a0]">Select a constraint or item to view details</p>
    </div>
  );
}
