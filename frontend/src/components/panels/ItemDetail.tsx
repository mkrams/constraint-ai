"use client";

import { Item, Constraint, EvaluationResult } from "@/lib/types";
import { useStore } from "@/lib/store";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getDomainColor, formatNumber } from "@/lib/utils";
import { AlertTriangle, CheckCircle, Zap } from "lucide-react";

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
  const setSelectedConstraintId = useStore((s) => s.setSelectedConstraintId);
  const setWhatIfMode = useStore((s) => s.setWhatIfMode);
  const setWhatIfParameter = useStore((s) => s.setWhatIfParameter);

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

  // Generate a health summary sentence
  const healthSummary = (() => {
    if (constraintStats.total === 0) return "No constraints are defined for this component.";
    if (constraintStats.failed === 0 && constraintStats.warnings === 0) {
      return `All ${constraintStats.total} constraints are passing. This component is operating within spec.`;
    }
    const parts: string[] = [];
    if (constraintStats.failed > 0) {
      parts.push(`${constraintStats.failed} constraint${constraintStats.failed > 1 ? "s are" : " is"} failing`);
    }
    if (constraintStats.warnings > 0) {
      parts.push(`${constraintStats.warnings} warning${constraintStats.warnings > 1 ? "s" : ""}`);
    }
    return `${parts.join(" and ")} out of ${constraintStats.total} total. ${constraintStats.failed > 0 ? "Action required." : "Worth monitoring."}`;
  })();

  const handleWhatIf = (parameterId: string) => {
    setWhatIfParameter(parameterId, null);
    setWhatIfMode(true);
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
          <span className="text-xs text-[#8888a0] capitalize">{item.domain}</span>
        </div>
        <h3 className="text-lg font-semibold text-[#e0e0e8] mb-1">
          {item.name}
        </h3>
        <p className="text-sm text-[#8888a0]">{item.item_type}</p>
      </div>

      {/* Health Summary - NL */}
      <div
        className="p-3 rounded text-sm leading-relaxed"
        style={{
          backgroundColor: constraintStats.failed > 0 ? "rgba(231, 76, 60, 0.06)" :
            constraintStats.warnings > 0 ? "rgba(243, 156, 18, 0.06)" : "rgba(0, 184, 148, 0.06)",
          borderLeft: `3px solid ${constraintStats.failed > 0 ? "#e74c3c" :
            constraintStats.warnings > 0 ? "#f39c12" : "#00b894"}`,
          color: "#d0d0d8",
        }}
      >
        {constraintStats.failed > 0 ? (
          <AlertTriangle size={14} className="inline mr-2 text-[#e74c3c]" style={{ marginTop: -2 }} />
        ) : constraintStats.warnings > 0 ? (
          <AlertTriangle size={14} className="inline mr-2 text-[#f39c12]" style={{ marginTop: -2 }} />
        ) : (
          <CheckCircle size={14} className="inline mr-2 text-[#00b894]" style={{ marginTop: -2 }} />
        )}
        {healthSummary}
      </div>

      {/* Constraint Health Grid */}
      <div className="card">
        <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
          Constraint Health
        </div>
        <div className="grid grid-cols-4 gap-2">
          <div className="text-center">
            <div className="text-lg font-bold text-[#e0e0e8]">{constraintStats.total}</div>
            <div className="text-xs text-[#8888a0]">Total</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#00b894]">{constraintStats.passed}</div>
            <div className="text-xs text-[#8888a0]">Pass</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#e74c3c]">{constraintStats.failed}</div>
            <div className="text-xs text-[#8888a0]">Fail</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#f39c12]">{constraintStats.warnings}</div>
            <div className="text-xs text-[#8888a0]">Warn</div>
          </div>
        </div>
      </div>

      {/* Parameters */}
      <div>
        <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
          Parameters ({item.parameters.length})
        </div>
        <div className="space-y-2">
          {item.parameters.map((param) => (
            <div key={param.id} className="card p-2 flex items-center justify-between group">
              <div className="flex-1">
                <div className="text-xs text-[#8888a0]">{param.name}</div>
                <div className="font-mono-values font-semibold text-[#e0e0e8]">
                  {formatNumber(param.value)} <span className="text-[#6c5ce7]">{param.unit}</span>
                </div>
              </div>
              <button
                onClick={() => handleWhatIf(param.id)}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-xs px-2 py-1 rounded text-[#6c5ce7] hover:bg-[#6c5ce7] hover:text-white"
                title={`What-if: ${param.name}`}
              >
                <Zap size={12} />
              </button>
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
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {itemConstraints.map((constraint) => {
              const evaluation = evaluationResults.find(
                (r) => r.constraint_id === constraint.id
              );
              return (
                <div
                  key={constraint.id}
                  className="card p-3 cursor-pointer hover:border-[#6c5ce7] transition-colors space-y-1"
                  onClick={() => setSelectedConstraintId(constraint.id)}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-[#e0e0e8]">
                      {constraint.name}
                    </span>
                    {evaluation && <StatusBadge status={evaluation.status} size="sm" />}
                  </div>
                  <div className="text-xs text-[#8888a0]">
                    {constraint.description}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
