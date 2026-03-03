"use client";

import { useCallback, useEffect, useMemo } from "react";
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";
import dagre from "@dagrejs/dagre";
import { useStore } from "@/lib/store";
import { ItemNode } from "./nodes/ItemNode";
import { ConstraintEdge } from "./edges/ConstraintEdge";
import { TraceEdge } from "./edges/TraceEdge";
import { Item, Trace, Constraint, EvaluationResult } from "@/lib/types";

const nodeTypes = { item: ItemNode };
const edgeTypes = { constraint: ConstraintEdge, trace: TraceEdge };

interface GraphProps {
  items: Item[];
  traces: Trace[];
  constraints: Constraint[];
  evaluationResults: EvaluationResult[];
}

export function Graph({
  items,
  traces,
  constraints,
  evaluationResults,
}: GraphProps) {
  const selectedNodeId = useStore((s) => s.selectedNodeId);
  const selectedConstraintId = useStore((s) => s.selectedConstraintId);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { fitView } = useReactFlow();

  // Create a mapping from parameter ID to constraint
  const parameterToConstraint = useMemo(() => {
    const map = new Map<string, Constraint>();
    constraints.forEach((constraint) => {
      map.set(constraint.source_parameter_id, constraint);
      map.set(constraint.target_parameter_id, constraint);
    });
    return map;
  }, [constraints]);

  // Create nodes and edges with dagre layout
  useEffect(() => {
    if (items.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    // Create graph for dagre layout
    const graph = new dagre.graphlib.Graph();
    graph.setGraph({ rankdir: "TB", nodesep: 50, ranksep: 80 });
    graph.setDefaultEdgeLabel(() => ({}));

    // Add nodes to graph
    items.forEach((item) => {
      const hasFailingConstraint = evaluationResults.some(
        (result) =>
          result.status === "fail" &&
          constraints.some(
            (c) =>
              c.id === result.constraint_id &&
              (item.parameters.some((p) => p.id === c.source_parameter_id) ||
                item.parameters.some((p) => p.id === c.target_parameter_id))
          )
      );

      graph.setNode(item.id, {
        width: 240,
        height: 200,
        hasFailingConstraint,
      });
    });

    // Add edges based on traces
    traces.forEach((trace) => {
      graph.setEdge(trace.source_item_id, trace.target_item_id);
    });

    // Run layout algorithm
    dagre.layout(graph);

    // Create ReactFlow nodes
    const flowNodes: Node[] = items.map((item) => {
      const nodeData = graph.node(item.id);
      return {
        id: item.id,
        data: { ...item, hasFailingConstraint: nodeData.hasFailingConstraint },
        position: { x: nodeData.x - 120, y: nodeData.y - 100 },
        type: "item",
        selected: item.id === selectedNodeId,
      };
    });

    // Create ReactFlow edges
    const flowEdges: Edge[] = [];

    // Trace edges
    traces.forEach((trace) => {
      flowEdges.push({
        id: `trace-${trace.id}`,
        source: trace.source_item_id,
        target: trace.target_item_id,
        type: "trace",
        data: {
          traceType: trace.trace_type,
          description: trace.description,
        },
      });
    });

    // Constraint edges - connect source parameter's item to target parameter's item
    constraints.forEach((constraint) => {
      const sourceParam = items
        .flatMap((i) => i.parameters)
        .find((p) => p.id === constraint.source_parameter_id);
      const targetParam = items
        .flatMap((i) => i.parameters)
        .find((p) => p.id === constraint.target_parameter_id);

      if (sourceParam && targetParam) {
        const sourceItem = items.find((i) =>
          i.parameters.some((p) => p.id === sourceParam.id)
        );
        const targetItem = items.find((i) =>
          i.parameters.some((p) => p.id === targetParam.id)
        );

        if (sourceItem && targetItem && sourceItem.id !== targetItem.id) {
          const evaluation = evaluationResults.find(
            (r) => r.constraint_id === constraint.id
          );

          flowEdges.push({
            id: `constraint-${constraint.id}`,
            source: sourceItem.id,
            target: targetItem.id,
            type: "constraint",
            data: {
              constraintId: constraint.id,
              constraintName: constraint.name,
              status: evaluation?.status || "unknown",
              ruleType: constraint.rule_type,
            },
            selected: constraint.id === selectedConstraintId,
          });
        }
      }
    });

    setNodes(flowNodes);
    setEdges(flowEdges);

    // Fit view after layout
    setTimeout(() => fitView({ padding: 0.2 }), 0);
  }, [items, traces, constraints, evaluationResults, selectedNodeId, selectedConstraintId, setNodes, setEdges, fitView]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      fitView
    >
      <Background color="#1e1e2e" gap={16} />
      <Controls />
    </ReactFlow>
  );
}
