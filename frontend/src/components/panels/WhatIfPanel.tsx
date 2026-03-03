"use client";

import { useState, useEffect } from "react";
import { Parameter, EvaluationResult } from "@/lib/types";
import { useStore } from "@/lib/store";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatNumber } from "@/lib/utils";
import { X } from "lucide-react";

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
        setWhatIfResults(response.directly_affected_constraints);
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
      // Refresh all data
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
      // Re-evaluate
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
      <div className="text-center py-8 text-[#8888a0]">
        Select a parameter to begin what-if analysis
      </div>
    );
  }

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

      {/* Parameter Info */}
      <div className="card">
        <div className="text-xs text-[#8888a0] mb-1">{currentParam.name}</div>
        <div className="font-mono-values font-semibold text-[#e0e0e8]">
          Current: {formatNumber(currentParam.value)} {currentParam.unit}
        </div>
      </div>

      {/* Value Slider */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <input
            type="range"
            min={currentParam.value * 0.5}
            max={currentParam.value * 1.5}
            step={currentParam.value * 0.01}
            value={whatIfValue !== null ? whatIfValue : currentParam.value}
            onChange={(e) => handleValueChange(parseFloat(e.target.value))}
            className="flex-1"
            style={{
              accentColor: "#6c5ce7",
            }}
          />
        </div>

        {/* Numeric Input */}
        <div className="flex gap-2">
          <input
            type="number"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              const num = parseFloat(e.target.value);
              if (!isNaN(num)) {
                handleValueChange(num);
              }
            }}
            className="input flex-1"
            step="0.1"
          />
          <span className="text-[#6c5ce7] font-semibold px-2 py-1">
            {currentParam.unit}
          </span>
        </div>
      </div>

      {/* Impact Summary */}
      {whatIfResults && (
        <div className="card space-y-2">
          <div className="text-xs text-[#8888a0] uppercase tracking-wider">
            Impact
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <div className="text-sm font-bold text-[#e0e0e8]">
                {whatIfResults.length}
              </div>
              <div className="text-xs text-[#8888a0]">Affected</div>
            </div>
            <div>
              <div className="text-sm font-bold text-[#e74c3c]">
                {whatIfResults.filter((r) => r.status === "fail").length}
              </div>
              <div className="text-xs text-[#8888a0]">Would Fail</div>
            </div>
          </div>
        </div>
      )}

      {/* Affected Constraints */}
      {whatIfResults && whatIfResults.length > 0 && (
        <div>
          <div className="text-xs text-[#8888a0] uppercase tracking-wider mb-2">
            Affected Constraints
          </div>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {whatIfResults.map((result) => (
              <div
                key={result.constraint_id}
                className="card text-xs p-2 flex items-center justify-between"
              >
                <span className="text-[#d0d0d8] truncate">
                  {result.constraint_id.slice(0, 8)}...
                </span>
                <StatusBadge status={result.status} size="sm" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="space-y-2 pt-2 border-t border-[#1e1e2e]">
        <button
          onClick={handleApplyChange}
          disabled={
            loading ||
            whatIfValue === null ||
            whatIfValue === currentParam.value
          }
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
