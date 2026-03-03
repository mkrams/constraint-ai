"use client";

import { useEffect, useState } from "react";
import { ReactFlowProvider } from "reactflow";
import { useStore } from "@/lib/store";
import { api } from "@/lib/api";
import { Header } from "@/components/Header";
import { LeftPanel } from "@/components/panels/LeftPanel";
import { RightPanel } from "@/components/panels/RightPanel";
import { Graph } from "@/components/Graph";

export default function Home() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [evaluating, setEvaluating] = useState(false);

  const items = useStore((s) => s.items);
  const parameters = useStore((s) => s.parameters);
  const traces = useStore((s) => s.traces);
  const constraints = useStore((s) => s.constraints);
  const evaluationResults = useStore((s) => s.evaluationResults);
  const loading = useStore((s) => s.loading);
  const error = useStore((s) => s.error);

  const setItems = useStore((s) => s.setItems);
  const setParameters = useStore((s) => s.setParameters);
  const setTraces = useStore((s) => s.setTraces);
  const setConstraints = useStore((s) => s.setConstraints);
  const setEvaluationResults = useStore((s) => s.setEvaluationResults);
  const setLoading = useStore((s) => s.setLoading);
  const setError = useStore((s) => s.setError);
  const setHealthStatus = useStore((s) => s.setHealthStatus);

  // Initial data load
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [itemsData, tracesData, constraintsData, evaluationData, healthData] =
          await Promise.all([
            api.getItems(),
            api.getTraces(),
            api.getConstraints(),
            api.evaluateAll(),
            api.getHealth(),
          ]);

        setItems(itemsData);
        setParameters(itemsData.flatMap((i) => i.parameters));
        setTraces(tracesData);
        setConstraints(constraintsData);
        setEvaluationResults(evaluationData.results);
        setHealthStatus({
          passed: evaluationData.passed,
          failed: evaluationData.failed,
          warnings: evaluationData.warnings,
          total: evaluationData.total_constraints,
        });

        setIsInitialized(true);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load data";
        setError(message);
        console.error("Data load error:", err);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [
    setItems,
    setParameters,
    setTraces,
    setConstraints,
    setEvaluationResults,
    setHealthStatus,
    setLoading,
    setError,
  ]);

  const handleEvaluateAll = async () => {
    try {
      setEvaluating(true);
      const evaluationData = await api.evaluateAll();
      setEvaluationResults(evaluationData.results);
      setHealthStatus({
        passed: evaluationData.passed,
        failed: evaluationData.failed,
        warnings: evaluationData.warnings,
        total: evaluationData.total_constraints,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Evaluation failed";
      setError(message);
      console.error("Evaluation error:", err);
    } finally {
      setEvaluating(false);
    }
  };

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0a0a0f] text-[#8888a0]">
        <div className="text-center space-y-4">
          <div className="animate-spin">
            <div className="w-8 h-8 border-2 border-[#6c5ce7] border-t-transparent rounded-full" />
          </div>
          <p>Loading constraint system...</p>
          {error && <p className="text-[#e74c3c]">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0f]">
      {/* Header */}
      <Header onEvaluateAll={handleEvaluateAll} loading={evaluating} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden gap-0">
        {/* Left Panel */}
        <div className="w-[280px] border-r border-[#1e1e2e] overflow-hidden">
          <LeftPanel items={items} evaluationResults={evaluationResults} />
        </div>

        {/* Graph Center */}
        <div className="flex-1 overflow-hidden">
          <ReactFlowProvider>
            <Graph
              items={items}
              traces={traces}
              constraints={constraints}
              evaluationResults={evaluationResults}
            />
          </ReactFlowProvider>
        </div>

        {/* Right Panel */}
        <div className="w-[340px] border-l border-[#1e1e2e] overflow-hidden">
          <div className="h-full flex flex-col bg-[#12121a]">
            <div className="panel-header border-b border-[#1e1e2e]">
              <h2 className="text-lg font-semibold text-[#e0e0e8]">Details</h2>
            </div>
            <div className="flex-1 overflow-y-auto">
              <RightPanel
                items={items}
                constraints={constraints}
                evaluationResults={evaluationResults}
                parameters={parameters}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-[#e74c3c] text-white px-4 py-3 rounded shadow-lg max-w-sm">
          {error}
        </div>
      )}
    </div>
  );
}
