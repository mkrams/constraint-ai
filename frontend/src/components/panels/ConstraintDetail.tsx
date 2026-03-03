"use client";

import { Constraint, EvaluationResult, Item, Parameter } from "@/lib/types";
import { useStore } from "@/lib/store";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { MarginBar } from "@/components/ui/MarginBar";
import { getRuleSymbol, formatNumber, getDomainColor } from "@/lib/utils";
import { explainConstraint, explainEvaluation, explainSeverity, formatRule } from "@/lib/explain";
import { useState } from "react";
import { AlertTriangle, Info, Zap, ArrowRight } from "lucide-react";

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
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const setWhatIfMode = useStore((s) => s.setWhatIfMode);
  const setWhatIfParameter = useStore((s) => s.setWhatIfParameter);

  const domains = Object.keys(constraint.domain_descriptions || {});
  const currentDomain = activeDomain && domains.includes(activeDomain) ? activeDomain : domains[0] || null;

  const handleWhatIf = (parameterId: string | undefined) => {
    if (parameterId) {
      setWhatIfParameter(parameterId, null);
      setWhatIfMode(true);
    }
  };

  const nlExplanation = explainConstraint(constraint, sourceParam, targetParam, sourceItem, targetItem);
  const evalExplanation = explainEvaluation(constraint, evaluation, sourceParam, targetParam);
  const severityExplanation = explainSeverity(constraint.severity);
  const ruleReadable = formatRule(constraint, sourceParam, targetParam);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-[#e0e0e8] mb-1">
          {constraint.name}
        </h3>
        <p className="text-sm text-[#d0d0d8] leading-relaxed">{constraint.description}</p>
      </div>

      {/* Status + Severity */}
      <div className="flex items-center gap-2 flex-wrap">
        {evaluation && <StatusBadge status={evaluation.status} />}
        <span
          className="badge"
          style={{
            backgroundColor: constraint.severity === "critical" ? "rgba(231, 76, 60, 0.1)" :
              constraint.severity === "error" ? "rgba(243, 156, 18, 0.1)" : "rgba(136, 136, 160, 0.1)",
            color: constraint.severity === "critical" ? "#e74c3c" :
              constraint.severity === "error" ? "#f39c12" : "#8888a0",
          }}
        >
          {constraint.severity}
        </span>
      </div>

      {/* Plain English Explanation */}
      <div
        className="p-3 rounded text-sm leading-relaxed"
        style={{
          backgroundColor: "rgba(108, 92, 231, 0.06)",
          borderLeft: "3px solid #6c5ce7",
          color: "#d0d0d8",
        }}
      >
        <Info size={14} className="inline mr-2 text-[#6c5ce7]" style={{ marginTop: -2 }} />
        {nlExplanation}
      </div>

      {/* Rule Visualization */}
      <div className="card space-y-3">
        <div className="text-xs text-[#8888a0] uppercase tracking-wider">
          Formal Rule
        </div>

        <div className="flex items-center gap-3">
          {sourceParam && sourceItem ? (
            <div className="flex-1 p-2 rounded" style={{ backgroundColor: "#0a0a0f" }}>
              <div className="text-xs font-semibold" style={{ color: getDomainColor(sourceItem.domain) }}>
                {sourceItem.short_id}
              </div>
              <div className="text-xs text-[#8888a0]">{sourceParam.name}</div>
              <div className="font-mono-values font-semibold text-[#e0e0e8]">
                {formatNumber(sourceParam.value)} {sourceParam.unit}
              </div>
            </div>
          ) : (
            <div className="flex-1 text-xs text-[#8888a0] p-2">N/A</div>
          )}

          <div className="flex flex-col items-center gap-1">
            <div className="text-xl font-bold text-[#6c5ce7]">
              {getRuleSymbol(constraint.rule_type)}
            </div>
            <ArrowRight size={12} className="text-[#8888a0]" />
          </div>

          {targetParam && targetItem ? (
            <div className="flex-1 p-2 rounded text-right" style={{ backgroundColor: "#0a0a0f" }}>
              <div className="text-xs font-semibold" style={{ color: getDomainColor(targetItem.domain) }}>
                {targetItem.short_id}
              </div>
              <div className="text-xs text-[#8888a0]">{targetParam.name}</div>
              <div className="font-mono-values font-semibold text-[#e0e0e8]">
                {formatNumber(targetParam.value)} {targetParam.unit}
              </div>
            </div>
          ) : (
            <div className="flex-1 text-xs text-[#8888a0] p-2 text-right">N/A</div>
          )}
        </div>

        <div className="text-xs font-mono-values text-[#8888a0] text-center">
          {ruleReadable}
        </div>
      </div>

      {/* Evaluation Result */}
      {evaluation && (
        <div className="space-y-2">
          <div className="text-xs text-[#8888a0] uppercase tracking-wider">
            Evaluation
          </div>
          <div
            className="p-3 rounded text-sm leading-relaxed"
            style={{
              backgroundColor: evaluation.status === "pass" ? "rgba(0, 184, 148, 0.06)" :
                evaluation.status === "fail" ? "rgba(231, 76, 60, 0.06)" : "rgba(243, 156, 18, 0.06)",
              borderLeft: `3px solid ${evaluation.status === "pass" ? "#00b894" :
                evaluation.status === "fail" ? "#e74c3c" : "#f39c12"}`,
              color: "#d0d0d8",
            }}
          >
            {evaluation.status === "fail" ? (
              <AlertTriangle size={14} className="inline mr-2 text-[#e74c3c]" style={{ marginTop: -2 }} />
            ) : (
              <Zap size={14} className="inline mr-2 text-[#00b894]" style={{ marginTop: -2 }} />
            )}
            {evalExplanation}
          </div>
          <MarginBar result={evaluation} />
        </div>
      )}

      {/* Severity Info */}
      <div className="text-xs text-[#8888a0] leading-relaxed p-2 rounded" style={{ backgroundColor: "#0a0a0f" }}>
        {severityExplanation}
      </div>

      {/* Domain Translations */}
      {domains.length > 0 && (
        <div>
          <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
            Cross-Domain View
          </div>
          <div className="flex gap-1 border-b border-[#1e1e2e] mb-2">
            {domains.map((domain) => (
              <button
                key={domain}
                onClick={() => setActiveDomain(domain)}
                className={`px-3 py-1.5 text-xs font-semibold transition-colors border-b-2 flex items-center gap-1.5 ${
                  currentDomain === domain
                    ? "border-[#6c5ce7] text-[#e0e0e8]"
                    : "border-transparent text-[#8888a0] hover:text-[#d0d0d8]"
                }`}
              >
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: getDomainColor(domain) }}
                />
                {domain.charAt(0).toUpperCase() + domain.slice(1)}
              </button>
            ))}
          </div>
          {constraint.domain_descriptions && currentDomain && (
            <div className="text-sm text-[#d0d0d8] leading-relaxed p-3 rounded" style={{ backgroundColor: "#1a1a28", border: "1px solid #1e1e2e" }}>
              {constraint.domain_descriptions[currentDomain]}
            </div>
          )}
        </div>
      )}

      {/* What-If Buttons */}
      <div className="space-y-2 pt-2 border-t border-[#1e1e2e]">
        <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-1">
          Explore Changes
        </div>
        {sourceParam && (
          <button
            onClick={() => handleWhatIf(sourceParam.id)}
            className="button w-full text-sm"
          >
            What-If: Adjust {sourceParam.name}
          </button>
        )}
        {targetParam && (
          <button
            onClick={() => handleWhatIf(targetParam.id)}
            className="button button-secondary w-full text-sm"
          >
            What-If: Adjust {targetParam.name}
          </button>
        )}
      </div>
    </div>
  );
}
