"use client";

import { useState, useEffect } from "react";
import { Parameter, EvaluationResult, WhatIfConstraint } from "@/lib/types";
import { useStore } from "@/lib/store";
import { api } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import { explainWhatIfImpact, getTransitionColor, getTransitionLabel } from "@/lib/explain";
import { X, AlertTriangle, CheckCircle, ArrowRight, TrendingUp, TrendingDown } from "lucide-react";

interface WhatIfPanelProps {
  parameters: Parameter[];
  evaluationResults: EvaluationResult[];
}

export function WhatIfPanel({
  parameters,
}: WhatIfPanelProps) {
  const whatIfParameterId = useStore((s) => s.whatIfParameterId);
  const whatIfValue = useStore((s) => s.whatIfValue);
  const whatIfResults = useStore((s) => s.whatIfResults);
  const setWhatIfParameter = useStore((s) => s.setWhatIfParameter);
  const setWhatIfResults = useStore((s) => s.setWhatIfResults);
  const clearWhatIf = useStore((s) => s.clearWhatIf);

  const [inputValue, setInputValue] = useState<string>("");
  const [loading, setLoadingLocal] = useState(false);
  const [summary, setSummary] = useState<string>("");
  const [feasible, setFeasible] = useState<boolean>(true);

  const currentParam = parameters.find((p) => p.id === whatIfParameterId);

  useEffect(() => {
    if (currentParam) {
      setInputValue(currentParam.value.toString());
    }
  }, [currentParam]);

  const handleValueChange = async (value: number) => {
    setWhatIfParameter(whatIfParameterId, value);
    setInputValue(value.toString());
    setLoadingLocal(true);

    try {
      if (whatIfParameterId) {
        const response = await api.whatIf(whatIfParameterId, value);
        setWhatIfResults(response.affected_constraints);
        setFeasible(response.feasible);

        const failingCount = response.affected_constraints.filter(
          (c) => c.current_status !== "fail" && c.proposed_status === "fail"
        ).length;
        const passingCount = response.affected_constraints.filter(
          (c) => c.current_status === "fail" && c.proposed_status !== "fail"
        ).length;

        const explanation = explainWhatIfImpact(
          currentParam?.name ?? "parameter",
          currentParam?.value ?? 0,
          value,
          currentParam?.unit ?? "",
          response.affected_constraints.length,
          failingCount,
          passingCount
        );
        setSummary(explanation);
      }
    } catch (error) {
      console.error("What-if analysis failed:", error);
    } finally {
      setLoadingLocal(false);
    }
  };

  const handleApplyChange = async () => {
    if (!whatIfParameterId || whatIfValue === null) return;

    setLoadingLocal(true);
    try {
      await api.updateParameter(whatIfParameterId, whatIfValue);
      const [items, constraints] = await Promise.all([
        api.getItems(),
        api.getConstraints(),
      ]);
      useStore.setState({
        items,
        constraints,
        parameters: items.flatMap((i) => i.parameters),
      });
      clearWhatIf();
      const evaluation = await api.evaluateAll();
      useStore.setState({ evaluationResults: evaluation.results });
    } catch (error) {
      console.error("Failed to apply change:", error);
    } finally {
      setLoadingLocal(false);
    }
  };

  if (!whatIfParameterId || !currentParam) {
    return (
      <div className="space-y-4 p-2">
        <div className="text-center py-8 text-[#8888a0]">
          <p className="mb-2">Select a parameter to begin what-if analysis.</p>
          <p className="text-xs">Click a constraint, then use the &quot;What-If&quot; buttons to explore how parameter changes affect the system.</p>
        </div>
      </div>
    );
  }

  const delta = whatIfValue !== null ? whatIfValue - currentParam.value : 0;
  const pctChange = currentParam.value !== 0 ? ((delta / currentParam.value) * 100) : 0;

  return (
    <div className="space-y-4 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#e0e0e8]">What-If Analysis</h3>
        <button
          onClick={clearWhatIf}
          className="p-1 hover:bg-[#1a1a28] rounded transition-colors"
        >
          <X size={16} className="text-[#8888a0]" />
        </button>
      </div>

      {/* Parameter Card */}
      <div className="card space-y-2">
        <div className="text-xs text-[#8888a0] uppercase tracking-wider">Adjusting</div>
        <div className="text-sm font-semibold text-[#e0e0e8]">{currentParam.name}</div>
        <div className="flex items-center gap-3">
          <div>
            <div className="text-xs text-[#8888a0]">Current</div>
            <div className="font-mono-values font-semibold text-[#e0e0e8]">
              {formatNumber(currentParam.value)} {currentParam.unit}
            </div>
          </div>
          {whatIfValue !== null && whatIfValue !== currentParam.value && (
            <>
              <ArrowRight size={14} className="text-[#6c5ce7]" />
              <div>
                <div className="text-xs text-[#8888a0]">Proposed</div>
                <div className="font-mono-values font-semibold" style={{ color: feasible ? "#00b894" : "#e74c3c" }}>
                  {formatNumber(whatIfValue)} {currentParam.unit}
                </div>
              </div>
              <div className="ml-auto flex items-center gap-1">
                {delta > 0 ? <TrendingUp size={12} className="text-[#6c5ce7]" /> : <TrendingDown size={12} className="text-[#6c5ce7]" />}
                <span className="text-xs font-mono-values text-[#8888a0]">
                  {delta > 0 ? "+" : ""}{formatNumber(delta)} ({pctChange > 0 ? "+" : ""}{pctChange.toFixed(1)}%)
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Value Controls */}
      <div className="space-y-2">
        <input
          type="range"
          min={currentParam.value * 0.5}
          max={currentParam.value * 1.5}
          step={currentParam.value * 0.01}
          value={whatIfValue !== null ? whatIfValue : currentParam.value}
          onChange={(e) => handleValueChange(parseFloat(e.target.value))}
          className="w-full"
          style={{ accentColor: "#6c5ce7" }}
        />
        <div className="flex gap-2">
          <input
            type="number"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              const num = parseFloat(e.target.value);
              if (!isNaN(num)) handleValueChange(num);
            }}
            className="input flex-1"
            step="0.1"
          />
          <span className="text-[#6c5ce7] font-semibold px-2 py-1 text-sm">
            {currentParam.unit}
          </span>
        </div>
      </div>

      {/* NL Summary */}
      {summary && (
        <div
          className="p-3 rounded text-sm leading-relaxed"
          style={{
            backgroundColor: feasible ? "rgba(0, 184, 148, 0.08)" : "rgba(231, 76, 60, 0.08)",
            borderLeft: `3px solid ${feasible ? "#00b894" : "#e74c3c"}`,
            color: "#d0d0d8",
          }}
        >
          {feasible ? (
            <CheckCircle size={14} className="inline mr-2 text-[#00b894]" style={{ marginTop: -2 }} />
          ) : (
            <AlertTriangle size={14} className="inline mr-2 text-[#e74c3c]" style={{ marginTop: -2 }} />
          )}
          {summary}
        </div>
      )}

      {/* Affected Constraints */}
      {whatIfResults && whatIfResults.length > 0 && (
        <div>
          <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
            Affected Constraints ({whatIfResults.length})
          </div>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {whatIfResults.map((result: WhatIfConstraint) => {
              const transColor = getTransitionColor(result.current_status, result.proposed_status);
              const transLabel = getTransitionLabel(result.current_status, result.proposed_status);
              return (
                <div
                  key={result.constraint_id}
                  className="card p-3 space-y-1"
                  style={{ borderLeftColor: transColor, borderLeftWidth: 3 }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-[#e0e0e8]">
                      {result.constraint_name}
                    </span>
                    <span
                      className="text-xs font-semibold px-2 py-0.5 rounded"
                      style={{
                        backgroundColor: `${transColor}15`,
                        color: transColor,
                      }}
                    >
                      {transLabel}
                    </span>
                  </div>
                  <div className="text-xs text-[#8888a0]">
                    {result.message}
                  </div>
                  {result.margin !== null && (
                    <div className="text-xs font-mono-values" style={{ color: transColor }}>
                      Margin: {result.margin.toFixed(1)}%
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="space-y-2 pt-2 border-t border-[#1e1e2e]">
        <button
          onClick={handleApplyChange}
          disabled={loading || whatIfValue === null || whatIfValue === currentParam.value}
          className="button w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Applying..." : "Apply Change"}
        </button>
        <button
          onClick={clearWhatIf}
          className="button-secondary w-full button"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
