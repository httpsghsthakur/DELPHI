import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CausalGraph } from "../components/report/CausalGraph";
import { parseGraph } from "../utils/graph";
describe("optional explicit graph interactions", () => {
  it("inspects returned nodes and edges and supports zoom/reset without creating relationships", () => {
    const graph = parseGraph({
      causal_graph: {
        nodes: [
          { id: "a", label: "Test event", kind: "observed" },
          { id: "b", label: "Test consequence", kind: "hypothetical" },
        ],
        edges: [{ id: "ab", source: "a", target: "b", kind: "hypothetical" }],
      },
    });
    render(<CausalGraph graph={graph} />);
    fireEvent.click(
      screen.getByRole("button", { name: "Inspect node Test event" }),
    );
    expect(
      screen.getByRole("dialog", { name: "Graph element" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Close details" }));
    fireEvent.keyDown(
      screen.getByRole("button", {
        name: "Inspect hypothetical relationship a to b",
      }),
      { key: "Enter" },
    );
    expect(
      screen.getByRole("dialog", { name: "Graph element" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Close details" }));
    fireEvent.click(screen.getByRole("button", { name: "Zoom in" }));
    fireEvent.click(screen.getByRole("button", { name: "Zoom out" }));
    fireEvent.click(screen.getByRole("button", { name: "Reset graph" }));
    expect(document.querySelector(".causal-graph > g")).toHaveAttribute(
      "transform",
      "translate(0,0) scale(1)",
    );
  });
});
