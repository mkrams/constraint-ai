"use client";

import { useStore } from "@/lib/store";
import { Activity, Zap } from "lucide-react";

interface HeaderProps {
  onEvaluateAll: () => Promise<void>;
  loading: boolean;
}

export function Header({ onEvaluateAll, loading }: HeaderProps) {
  const healthStatus = useStore((s) => s.healthStatus);
  const whatIfMode = useStore((s) => s.whatIfMode);
  const setWhatIfMode = useStore((s) => s.setWhatIfMode);
  const domainFilter = useStore((s) => s.domainFilter);
  const setDomainFilter = useStore((s) => s.setDomainFilter);

  const domains = ["electrical", "thermal", "mechanical", "systems", "software"];

  return (
    <header className="bg-[#0a0a0f] border-b border-[#1e1e2e] px-6 py-3">
      <div className="flex items-center justify-between gap-6">
        {/* Logo/Title */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-[#6c5ce7] flex items-center justify-center">
            <Zap size={20} className="text-white" />
          </div>
          <h1 className="text-xl font-bold text-[#e0e0e8]">Constraint AI</h1>
        </div>

        {/* Health Summary */}
        {healthStatus && (
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1">
              <Activity size={14} className="text-[#00b894]" />
              <span className="text-[#8888a0]">{healthStatus.passed}</span>
              <span className="text-[#00b894]">pass</span>
            </div>
            <div className="flex items-center gap-1">
              <Activity size={14} className="text-[#e74c3c]" />
              <span className="text-[#8888a0]">{healthStatus.failed}</span>
              <span className="text-[#e74c3c]">fail</span>
            </div>
            <div className="flex items-center gap-1">
              <Activity size={14} className="text-[#f39c12]" />
              <span className="text-[#8888a0]">{healthStatus.warnings}</span>
              <span className="text-[#f39c12]">warn</span>
            </div>
          </div>
        )}

        {/* Domain Filters */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setDomainFilter(null)}
            className={`text-xs px-3 py-1.5 rounded transition-colors ${
              domainFilter === null
                ? "bg-[#6c5ce7] text-white"
                : "text-[#8888a0] hover:text-[#e0e0e8]"
            }`}
          >
            All
          </button>
          {domains.map((domain) => (
            <button
              key={domain}
              onClick={() => setDomainFilter(domain)}
              className={`text-xs px-3 py-1.5 rounded transition-colors capitalize ${
                domainFilter === domain
                  ? "bg-[#6c5ce7] text-white"
                  : "text-[#8888a0] hover:text-[#e0e0e8]"
              }`}
            >
              {domain}
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setWhatIfMode(!whatIfMode)}
            className={`button button-small ${
              whatIfMode ? "bg-[#6c5ce7]" : "button-secondary"
            }`}
          >
            {whatIfMode ? "Exit What-If" : "What-If Mode"}
          </button>
          <button
            onClick={onEvaluateAll}
            disabled={loading}
            className="button button-small disabled:opacity-50"
          >
            {loading ? "Evaluating..." : "Evaluate All"}
          </button>
        </div>
      </div>
    </header>
  );
}
