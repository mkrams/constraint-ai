"use client";

import { Item, EvaluationResult } from "@/lib/types";
import { useStore } from "@/lib/store";
import { getDomainColor, formatNumber } from "@/lib/utils";

interface LeftPanelProps {
  items: Item[];
  evaluationResults: EvaluationResult[];
}

export function LeftPanel({ items, evaluationResults }: LeftPanelProps) {
  const selectedNodeId = useStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useStore((s) => s.setSelectedNodeId);
  const domainFilter = useStore((s) => s.domainFilter);
  const setDomainFilter = useStore((s) => s.setDomainFilter);

  const filteredItems = domainFilter
    ? items.filter((i) => i.domain === domainFilter)
    : items;

  // Count unique domains
  const domains = Array.from(new Set(items.map((i) => i.domain)));

  // Helper to check if item has failing constraint
  const getItemHealthStatus = (item: Item) => {
    const itemConstraintIds = evaluationResults
      .filter(
        (r) =>
          r.status === "fail" &&
          items
            .find((i) => i.id === item.id)
            ?.parameters.some(
              (_p) =>
                // Would need constraint data to properly check, for now just check if evaluation exists
                true
            )
      )
      .map((r) => r.constraint_id);
    return itemConstraintIds.length > 0;
  };

  return (
    <div className="panel h-full flex flex-col">
      {/* Header */}
      <div className="panel-header border-b border-[#1e1e2e]">
        <h2 className="text-lg font-semibold text-[#e0e0e8] mb-3">Items</h2>

        {/* Domain Filters */}
        <div className="space-y-2">
          <button
            onClick={() => setDomainFilter(null)}
            className={`w-full text-xs py-1.5 px-2 rounded transition-colors text-left ${
              domainFilter === null
                ? "bg-[#6c5ce7] text-white"
                : "bg-[#1a1a28] text-[#8888a0] hover:bg-[#20202e]"
            }`}
          >
            All ({items.length})
          </button>
          {domains.map((domain) => {
            const count = items.filter((i) => i.domain === domain).length;
            return (
              <button
                key={domain}
                onClick={() => setDomainFilter(domain)}
                className={`w-full text-xs py-1.5 px-2 rounded transition-colors text-left flex items-center gap-2 ${
                  domainFilter === domain
                    ? "bg-[#6c5ce7] text-white"
                    : "bg-[#1a1a28] text-[#8888a0] hover:bg-[#20202e]"
                }`}
              >
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: getDomainColor(domain) }}
                />
                <span className="capitalize flex-1">{domain}</span>
                <span className="text-[#6888a0]">({count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Items List */}
      <div className="flex-1 overflow-y-auto panel-content space-y-2">
        {filteredItems.length === 0 ? (
          <div className="text-center py-8 text-[#8888a0]">No items</div>
        ) : (
          filteredItems.map((item) => {
            const hasFailure = getItemHealthStatus(item);
            return (
              <div
                key={item.id}
                onClick={() => setSelectedNodeId(item.id)}
                className={`card cursor-pointer transition-all p-3 ${
                  selectedNodeId === item.id ? "selected" : ""
                }`}
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <div
                      className="text-xs font-bold uppercase tracking-wider"
                      style={{ color: getDomainColor(item.domain) }}
                    >
                      {item.short_id}
                    </div>
                    <div className="text-sm font-semibold text-[#e0e0e8] truncate">
                      {item.name}
                    </div>
                  </div>
                  {hasFailure && (
                    <div
                      className="w-2 h-2 rounded-full flex-shrink-0 mt-1"
                      style={{ backgroundColor: "#e74c3c" }}
                      title="Constraint failure"
                    />
                  )}
                </div>

                {/* Parameters */}
                <div className="space-y-1">
                  {item.parameters.slice(0, 3).map((param) => (
                    <div
                      key={param.id}
                      className="text-xs bg-[#0a0a0f] px-2 py-1 rounded"
                    >
                      <div className="text-[#8888a0]">{param.name}</div>
                      <div className="font-mono-values font-semibold text-[#e0e0e8]">
                        {formatNumber(param.value)} <span className="text-[#6c5ce7]">{param.unit}</span>
                      </div>
                    </div>
                  ))}
                  {item.parameters.length > 3 && (
                    <div className="text-xs text-[#8888a0] px-2 py-1">
                      +{item.parameters.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
