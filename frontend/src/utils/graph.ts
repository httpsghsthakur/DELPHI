import type { CausalGraph as Graph, JsonObject } from "../api/types";
export function parseGraph(event: JsonObject): Graph | null {
  const graph = event.causal_graph;
  if (!graph || typeof graph !== "object" || Array.isArray(graph)) return null;
  if (!Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) return null;
  const kinds = ["observed", "inferred", "hypothetical"];
  if (
    !graph.nodes.every(
      (n) =>
        n &&
        typeof n === "object" &&
        !Array.isArray(n) &&
        typeof n.id === "string" &&
        typeof n.label === "string" &&
        kinds.includes(String(n.kind)),
    )
  )
    return null;
  if (
    !graph.edges.every(
      (e) =>
        e &&
        typeof e === "object" &&
        !Array.isArray(e) &&
        typeof e.id === "string" &&
        typeof e.source === "string" &&
        typeof e.target === "string" &&
        kinds.includes(String(e.kind)),
    )
  )
    return null;
  const typed = graph as unknown as Graph;
  if (
    new Set(typed.nodes.map((n) => n.id)).size !== typed.nodes.length ||
    !typed.edges.every(
      (e) =>
        typed.nodes.some((n) => n.id === e.source) &&
        typed.nodes.some((n) => n.id === e.target),
    )
  )
    return null;
  return typed;
}
