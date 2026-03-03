"use client";

import { Item, Constraint, EvaluationResult } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getDomainColor, formatNumber } from "@/lib/utils";

interface ItemDetailProps {
  item: Item;
  constraints: Constraint[];
  evaluationResults: EvaluationResult[];
}

export function ItemDetail({
  item,
  constraints,
  evaluationResults,
}: ItemDetailProps) {
  const itemConstraints = constraints.filter(
    (c) =>
      item.parameters.some((p) => p.id === c.source_parameter_id) ||
      item.parameters.some((p) => p.id === c.target_parameter_id)
  );

  const constraintStats = {
    total: itemConstraints.length,
    passed: evaluationResults.filter(
      (r) =>
        r.status === "pass" &&
        itemConstraints.some((c) => c.id === r.constraint_id)
    ).length,
    failed: evaluationResults.filter(
      (r) =>
        r.status === "fail" &&
        itemConstraints.some((c) => c.id === r.constraint_id)
    ).length,
    warnings: evaluationResults.filter(
      (r) =>
        r.status === "warning" &&
        itemConstraints.some((c) => c.id === r.constraint_id)
    ).length,
  };

  return (
    <div className="space-y-4">
      {/* Item Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: getDomainColor(item.domain) }}
          />
          <div
            className="text-xs font-bold uppercase tracking-wider"
            style={{ color: getDomainColor(item.domain) }}
          >
            {item.short_id}
          </div>
        </div>
        <h3 className="text-lg font-semibold text-[#e0e0e8] mb-1">
          {item.name}
        </h3>
        <p className="text-sm text-[#8888a0]">{item.item_type}</p>
      </div>

      {/* Constraint Summary */}
      <div className="card">
        <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
          Constraint Health
        </div>
        <div className="grid grid-cols-4 gap-2">
          <div className="text-center">
            <div className="text-lg font-bold text-[#e0e0e8]">
              {constraintStats.total}
            </div>
            <div className="text-xs text-[#8888a0]">Total</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#00b894]">
              {constraintStats.passed}
            </div>
            <div className="text-xs text-[#8888a0]">Pass</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#e74c3c]">
              {constraintStats.failed}
            </div>
            <div className="text-xs text-[#8888a0]">Fail</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#f39c12]">
              {constraintStats.warnings}
            </div>
            <div className="text-xs text-[#8888a0]">Warn</div>
          </div>
        </div>
      </div>

      {/* Parameters */}
      <div>
        <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
          Parameters
        </div>
        <div className="space-y-2">
          {item.parameters.map((param) => (
            <div key={param.id} className="card">
              <div className="text-xs text-[#8888a0] mb-1">{param.name}</div>
              <div className="font-mono-values font-semibold text-[#e0e0e8]">
                {formatNumber(param.value)} <span className="text-[#6c5ce7]">{param.unit}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Related Constraints */}
      {itemConstraints.length > 0 && (
        <div>
          <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
            Related Constraints
          </div>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {itemConstraints.map((constraint) => {
              const evaluation = evaluationResults.find(
                (r) => r.constraint_id === constraint.id
              );
              return (
                <div
                  key={constraint.id}
                  className="card text-xs p-2 flex items-center justify-between"
                >
                  <span className="text-[#d0d0d8] truncate">
                    {constraint.name}
                  </span>
                  {evaluation && (
                    <StatusBadge status={evaluation.status} size="sm" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
