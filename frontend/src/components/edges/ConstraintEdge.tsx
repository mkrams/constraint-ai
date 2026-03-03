"use client";

import {
  EdgeProps,
  getStraightPath,
  EdgeLabelRenderer,
} from "reactflow";
import { getStatusColor, getRuleSymbol } from "@/lib/utils";
import { useStore } from "@/lib/store";

interface ConstraintEdgeData {
  constraintId: string;
  constraintName: string;
  status: "pass" | "fail" | "warning" | "unknown";
  ruleType: string;
}

export function ConstraintEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data,
  selected,
}: EdgeProps<ConstraintEdgeData>) {
  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
  });

  const status = data?.status ?? "unknown";
  const constraintId = data?.constraintId ?? id;
  const constraintName = data?.constraintName ?? "";
  const ruleType = data?.ruleType ?? "eq";
  const color = getStatusColor(status);
  const setSelectedConstraintId = useStore((s) => s.setSelectedConstraintId);

  return (
    <>
      <path
        id={id}
        d={edgePath}
        stroke={color}
        strokeWidth={selected ? 3 : 2}
        fill="none"
        className="cursor-pointer transition-all"
        onClick={() => setSelectedConstraintId(constraintId)}
        style={{
          opacity: selected ? 1 : 0.7,
          filter: selected ? `drop-shadow(0 0 8px ${color})` : undefined,
        }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: "all",
          }}
          className="cursor-pointer"
        >
          <div
            className="px-2 py-1 rounded text-xs font-bold font-mono-values"
            style={{
              backgroundColor: "#1a1a28",
              border: `1px solid ${color}`,
              color: color,
            }}
            onClick={() => setSelectedConstraintId(constraintId)}
            title={constraintName}
          >
            {getRuleSymbol(ruleType)}
          </div>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
