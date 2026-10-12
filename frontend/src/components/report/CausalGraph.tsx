import { useCallback, useEffect, useRef, useState } from "react";
import { select, zoom, zoomIdentity } from "d3";
import { Minus, Plus, RotateCcw } from "lucide-react";
import type {
  CausalGraph as Graph,
  GraphEdge,
  GraphNode,
} from "../../api/types";
import { Drawer, EmptyState, Metadata } from "../ui/Primitives";
export function CausalGraph({ graph }: { graph: Graph | null }) {
  const ref = useRef<SVGSVGElement>(null),
    group = useRef<SVGGElement>(null);
  const [selected, setSelected] = useState<GraphNode | GraphEdge | null>(null);
  const close = useCallback(() => setSelected(null), []);
  const behavior = useRef(
    zoom<SVGSVGElement, unknown>()
      .extent([
        [0, 0],
        [800, 480],
      ])
      .scaleExtent([0.3, 3]),
  );
  useEffect(() => {
    if (!ref.current || !group.current) return;
    const g = select(group.current);
    const svg = select(ref.current);
    svg.call(
      behavior.current.on("zoom", (e) =>
        g.attr("transform", e.transform.toString()),
      ),
    );
    return () => {
      svg.on(".zoom", null);
    };
  }, [graph]);
  if (!graph?.nodes.length)
    return (
      <EmptyState
        title="Causal relationships are not returned"
        description="The current API supplies forecast trajectories without explicit causal nodes or edges. A trajectory alone does not establish a causal relationship."
      />
    );
  const positions = graph.nodes.map((n, i) => ({
    ...n,
    x: 90 + (i % 3) * 240,
    y: 90 + Math.floor(i / 3) * 150,
  }));
  function scale(factor: number) {
    if (ref.current) select(ref.current).call(behavior.current.scaleBy, factor);
  }
  return (
    <>
      <div className="graph-toolbar">
        <div className="graph-legend">
          <span>— Observed</span>
          <span>– – Inferred</span>
          <span>··· Hypothetical</span>
        </div>
        <div>
          <button
            className="icon-button"
            aria-label="Zoom in"
            onClick={() => scale(1.3)}
          >
            <Plus size={17} />
          </button>
          <button
            className="icon-button"
            aria-label="Zoom out"
            onClick={() => scale(0.7)}
          >
            <Minus size={17} />
          </button>
          <button
            className="icon-button"
            aria-label="Reset graph"
            onClick={() => {
              if (ref.current)
                select(ref.current).call(
                  behavior.current.transform,
                  zoomIdentity,
                );
            }}
          >
            <RotateCcw size={16} />
          </button>
        </div>
      </div>
      <svg
        className="causal-graph"
        ref={ref}
        viewBox="0 0 800 480"
        aria-label="Causal relationships"
        role="img"
      >
        <g ref={group}>
          {graph.edges.map((edge) => {
            const s = positions.find((n) => n.id === edge.source)!,
              t = positions.find((n) => n.id === edge.target)!;
            return (
              <g
                key={edge.id}
                className="graph-edge"
                role="button"
                tabIndex={0}
                aria-label={`Inspect ${edge.kind} relationship ${edge.source} to ${edge.target}`}
                onClick={() => setSelected(edge)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setSelected(edge);
                  }
                }}
              >
                <line
                  x1={s.x}
                  y1={s.y}
                  x2={t.x}
                  y2={t.y}
                  strokeDasharray={
                    edge.kind === "inferred"
                      ? "8 5"
                      : edge.kind === "hypothetical"
                        ? "2 4"
                        : undefined
                  }
                />
              </g>
            );
          })}
          {positions.map((n) => (
            <g
              className={`graph-node ${n.kind}`}
              role="button"
              tabIndex={0}
              aria-label={`Inspect node ${n.label}`}
              key={n.id}
              transform={`translate(${n.x},${n.y})`}
              onClick={() => setSelected(n)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setSelected(n);
                }
              }}
            >
              <rect x="-70" y="-25" width="170" height="55" rx="4" />
              <text x="15" textAnchor="middle" dy="5">
                {n.label.slice(0, 23)}
              </text>
            </g>
          ))}
        </g>
      </svg>
      {selected && (
        <Drawer title="Graph element" onClose={close}>
          <Metadata data={{ ...selected }} />
        </Drawer>
      )}
    </>
  );
}
