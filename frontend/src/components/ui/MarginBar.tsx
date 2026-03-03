import { EvaluationResult } from "@/lib/types";
import { getStatusColor } from "@/lib/utils";

interface MarginBarProps {
  result: EvaluationResult;
  height?: number;
}

export function MarginBar({ result, height = 8 }: MarginBarProps) {
  const margin = result.margin ?? 0;
  const percentage = Math.min(100, Math.max(0, margin));
  const color = getStatusColor(result.status);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">Margin</span>
        <span className="font-mono-values font-semibold" style={{ color }}>
          {margin.toFixed(1)}%
        </span>
      </div>
      <div className="w-full bg-gray-900 rounded-full overflow-hidden" style={{ height }}>
        <div
          className="h-full transition-all duration-300"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
            opacity: 0.8,
          }}
        />
      </div>
    </div>
  );
}
