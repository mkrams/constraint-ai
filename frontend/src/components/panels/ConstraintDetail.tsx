"use client";

import { Constraint, EvaluationResult, Item, Parameter } from "@/lib/types";
import { useStore } from "@/lib/store";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { MarginBar } from "@/components/ui/MarginBar";
import { getRuleSymbol, formatNumber } from "@/lib/utils";
import { useState } from "react";

interface ConstraintDetailProps {
  constraint: Constraint;
  evaluation: EvaluationResult | undefined;
  sourceParam: Parameter | undefined;
  targetParam: Parameter | undefined;
  sourceItem: Item | undefined;
  targetItem: Item | undefined;
}

export function ConstraintDetail({
  constraint,
  evaluation,
  sourceParam,
  targetParam,
  sourceItem,
  targetItem,
}: ConstraintDetailProps) {
  const [activeDomain, setActiveDomain] = useState<string>("electrical");
  const setWhatIfMode = useStore((s) => s.setWhatIfMode);
  const setWhatIfParameter = useStore((s) => s.setWhatIfParameter);

  const domains = Object.keys(constraint.domain_descriptions || {});

  const handleWhatIf = (parameterId: string | undefined) => {
    if (parameterId) {
      setWhatIfParameter(parameterId, null);
      setWhatIfMode(true);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-[#e0e0e8] mb-2">
          {constraint.name}
        </h3>
        <p className="text-sm text-[#8888a0]">{constraint.description}</p>
      </div>

      {/* Status and Severity */}
      <div className="flex gap-2">
        {evaluation && <StatusBadge status={evaluation.status} />}
        <span className="badge" style={{ backgroundColor: "#1a1a28", color: "#8888a0" }}>
          {constraint.severity}
        </span>
      </div>

      {/* Rule Visualization */}
      <div className="card space-y-2">
        <div className="text-xs text-[#8888a0] uppercase tracking-wider">
          Rule
        </div>
        <div className="flex items-center justify-between gap-2">
          {sourceParam && sourceItem ? (
            <div className="flex-1">
              <div className="text-xs text-[#8888a0]">{sourceItem.short_id}</div>
              <div className="font-mono-values font-semibold text-[#e0e0e8]">
                {formatNumber(sourceParam.value)} {sourceParam.unit}
              </div>
            </div>
          ) : (
            <div className="text-xs text-[#8888a0]">N/A</div>
          )}

          <div className="text-xl font-bold text-[#6c5ce7]">
            {getRuleSymbol(constraint.rule_type)}
          </div>

          {targetParam && targetItem ? (
            <div className="flex-1 text-right">
              <div className="text-xs text-[#8888a0]">{targetItem.short_id}</div>
              <div className="font-mono-values font-semibold text-[#e0e0e8]">
                {formatNumber(targetParam.value)} {targetParam.unit}
              </div>
            </div>
          ) : (
            <div className="text-xs text-[#8888a0]">N/A</div>
          )}
        </div>

        {evaluation && (
          <div className="pt-2 border-t border-[#1e1e2e]">
            <div className="text-xs text-[#8888a0]">Evaluation</div>
            <div className="font-mono-values text-sm text-[#e0e0e8] mt-1">
              {evaluation.message ?? "No message"}
            </div>
          </div>
        )}
      </div>

      {/* Margin Bar */}
      {evaluation && <MarginBar result={evaluation} />}

      {/* Domain Descriptions */}
      {domains.length > 0 && (
        <div>
          <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
            Domain Details
          </div>
          <div className="flex gap-1 border-b border-[#1e1e2e] mb-2">
            {domains.map((domain) => (
              <button
                key={domain}
                onClick={() => setActiveDomain(domain)}
                className={`px-3 py-1.5 text-xs font-semibold transition-colors border-b-2 ${
                  activeDomain === domain
                    ? "border-[#6c5ce7] text-[#e0e0e8]"
                    : "border-transparent text-[#8888a0]"
                }`}
              >
                {domain.charAt(0).toUpperCase() + domain.slice(1)}
              </button>
            ))}
          </div>
          {constraint.domain_descriptions && (
            <div className="text-sm text-[#d0d0d8] bg-[#1a1a28] p-3 rounded border border-[#1e1e2e]">
              {constraint.domain_descriptions[activeDomain]}
            </div>
          )}
        </div>
      )}

      {/* What-If Buttons */}
      <div className="space-y-2">
        {sourceParam && (
          <button
            onClick={() => handleWhatIf(sourceParam.id)}
            className="button w-full"
          >
            What-If: {sourceParam.name}
          </button>
        )}
        {targetParam && (
          <button
            onClick={() => handleWhatIf(targetParam.id)}
            className="button w-full"
          >
            What-If: {targetParam.name}
          </button>
        )}
      </div>
    </div>
  );
}
