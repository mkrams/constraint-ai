"use client";

import { Handle, Position, NodeProps } from "reactflow";
import { Item } from "@/lib/types";
import { getDomainColor, formatNumber } from "@/lib/utils";
import { useStore } from "@/lib/store";

interface ItemNodeData extends Item {
  hasFailingConstraint?: boolean;
}

export function ItemNode({
  data,
  selected,
}: NodeProps<ItemNodeData>) {
  const domainColor = getDomainColor(data.domain);
  const setSelectedNodeId = useStore((s) => s.setSelectedNodeId);

  return (
    <div
      className={`rounded-lg border-2 min-w-[240px] cursor-pointer transition-all ${
        selected ? "border-[#6c5ce7] shadow-lg" : "border-[#1e1e2e]"
      }`}
      style={{
        backgroundColor: "#1a1a28",
        boxShadow: selected ? "0 0 20px rgba(108, 92, 231, 0.3)" : undefined,
      }}
      onClick={() => setSelectedNodeId(data.id)}
    >
      {/* Header */}
      <div
        className="px-3 py-2 border-b border-[#1e1e2e] flex items-center gap-2"
        style={{ backgroundColor: domainColor + "15" }}
      >
        <div
          className="w-3 h-3 rounded-full flex-shrink-0"
          style={{ backgroundColor: domainColor }}
        />
        <div className="min-w-0 flex-1">
          <div
            className="text-xs font-bold uppercase tracking-wider text-[#8888a0]"
            style={{ color: domainColor }}
          >
            {data.short_id}
          </div>
          <div className="text-sm font-semibold text-[#e0e0e8] truncate">
            {data.name}
          </div>
        </div>
        {data.hasFailingConstraint && (
          <div
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: "#e74c3c" }}
            title="Constraint failure"
          />
        )}
      </div>

      {/* Parameters */}
      <div className="px-3 py-2 space-y-1.5">
        {data.parameters.slice(0, 4).map((param) => (
          <div
            key={param.id}
            className="text-xs cursor-pointer hover:opacity-75 transition-opacity"
            onClick={(e) => {
              e.stopPropagation();
              useStore.setState({ selectedParameterId: param.id });
            }}
          >
            <div className="text-[#8888a0]">{param.name}</div>
            <div className="font-mono-values font-semibold text-[#e0e0e8]">
              {formatNumber(param.value)} <span className="text-[#6c5ce7]">{param.unit}</span>
            </div>
          </div>
        ))}
        {data.parameters.length > 4 && (
          <div className="text-xs text-[#8888a0] italic">
            +{data.parameters.length - 4} more
          </div>
        )}
      </div>

      {/* Handles */}
      <Handle position={Position.Top} type="target" />
      <Handle position={Position.Bottom} type="source" />
    </div>
  );
}
