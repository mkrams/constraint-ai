"use client";

import { EdgeProps, getStraightPath, EdgeLabelRenderer } from "reactflow";

interface TraceEdgeData {
  traceType: string;
  description: string;
}

export function TraceEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data,
}: EdgeProps<TraceEdgeData>) {
  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
  });

  return (
    <>
      <path
        id={id}
        d={edgePath}
        stroke="#4a4a5e"
        strokeWidth={1.5}
        strokeDasharray="5,5"
        fill="none"
        style={{ opacity: 0.5 }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: "none",
          }}
        >
          <div
            className="px-2 py-0.5 rounded text-xs text-[#8888a0]"
            style={{
              backgroundColor: "#0a0a0f",
              border: "1px solid #1e1e2e",
            }}
            title={data?.description ?? ""}
          >
            {data?.traceType ?? ""}
          </div>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
