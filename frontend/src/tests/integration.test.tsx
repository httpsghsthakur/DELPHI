import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import App from "../App";
import { apiClient } from "../api/client";
import { useAnalysisStore } from "../state/analysisStore";
import { health, models, report, research } from "./fixtures";
vi.mock("../api/client", () => ({
  apiClient: {
    baseUrl: "/api",
    getHealth: vi.fn(),
    getModels: vi.fn(),
    analyze: vi.fn(),
    research: vi.fn(),
    historicalSearch: vi.fn(),
    startBacktest: vi.fn(),
    getBacktest: vi.fn(),
  },
}));
beforeEach(() => {
  cleanup();
  vi.resetAllMocks();
  window.history.replaceState({}, "", "/");
  useAnalysisStore.setState({
    report: null,
    history: [],
    researchHistory: [],
    loading: false,
    error: null,
    systemStatus: null,
    models: null,
    healthError: null,
    modelsError: null,
    checkingHealth: false,
  });
  vi.mocked(apiClient.getHealth).mockResolvedValue(health);
  vi.mocked(apiClient.getModels).mockResolvedValue(models);
  vi.mocked(apiClient.analyze).mockResolvedValue(report);
});
function openComposer() {
  window.history.replaceState({}, "", "/analysis/new");
  render(<App />);
}
function fillDates() {
  fireEvent.change(screen.getByLabelText("Publication date"), {
    target: { value: "2026-08-01T00:00" },
  });
  fireEvent.change(screen.getByLabelText("Prediction cutoff"), {
    target: { value: "2026-09-01T00:00" },
  });
}
describe("frontend contract integration", () => {
  it("starts honestly empty and all sidebar destinations are real routes", async () => {
    render(<App />);
    expect(screen.getByText(/No analysis has been run/)).toBeInTheDocument();
    expect(document.querySelectorAll("nav a")).toHaveLength(13);
    expect(document.querySelector('nav a[href="#"]')).toBeNull();
    await screen.findByText(/SYNTHETIC execution/);
    fireEvent.click(screen.getByRole("link", { name: "Settings" }));
    expect(
      await screen.findByText("Configuration editing unavailable"),
    ).toBeInTheDocument();
    expect(screen.queryByText("Save")).toBeNull();
  });
  it("prevents empty inputs and temporal leakage, adds/removes domains, and submits exact fields", async () => {
    openComposer();
    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));
    expect(
      await screen.findByText("Article or event text is required."),
    ).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(/Article or event description/), {
      target: { value: "Test event context" },
    });
    fillDates();
    fireEvent.change(screen.getByLabelText("Publication date"), {
      target: { value: "2026-10-01T00:00" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));
    expect(await screen.findByText(/TEMPORAL LEAKAGE/)).toBeInTheDocument();
    expect(apiClient.analyze).not.toHaveBeenCalled();
    fillDates();
    fireEvent.change(screen.getByLabelText("Domains"), {
      target: { value: "security" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add" }));
    fireEvent.click(screen.getByRole("button", { name: "Remove geopolitics" }));
    fireEvent.change(screen.getByLabelText("Forecast horizon"), {
      target: { value: "90" },
    });
    fireEvent.click(screen.getByLabelText(/Live web research/));
    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));
    await waitFor(() =>
      expect(apiClient.analyze).toHaveBeenCalledWith(
        expect.objectContaining({
          text: "Test event context",
          domain: "security",
          forecast_horizon: 90,
          live_research: true,
          publication_timestamp: new Date("2026-08-01T00:00").toISOString(),
          prediction_information_cutoff: new Date(
            "2026-09-01T00:00",
          ).toISOString(),
        }),
        expect.any(String),
      ),
    );
    expect(
      await screen.findByRole("heading", { name: "Analysis report" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/backend used synthetic components/),
    ).toBeInTheDocument();
    expect(screen.getByText(/not validated probabilities/)).toBeInTheDocument();
    expect(screen.queryByText("70%")).toBeNull();
    fireEvent.click(screen.getByRole("tab", { name: "Evidence" }));
    expect(await screen.findByText("Test evidence claim")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /test-source/ })).toHaveAttribute(
      "href",
      "https://example.com/evidence",
    );
    fireEvent.click(screen.getByRole("button", { name: "Inspect" }));
    expect(
      screen.getByRole("dialog", { name: "Evidence detail" }),
    ).toBeInTheDocument();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).toBeNull();
    fireEvent.click(screen.getByRole("tab", { name: "Indicators" }));
    expect(screen.getByText("test-indicator")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "Provenance" }));
    expect(screen.getByText("test-dataset")).toBeInTheDocument();
  });
  it("shows genuine pending and failure states without injecting success", async () => {
    let reject!: (error: Error) => void;
    vi.mocked(apiClient.analyze).mockReturnValue(
      new Promise((_, r) => {
        reject = r;
      }),
    );
    openComposer();
    fillDates();
    fireEvent.change(screen.getByLabelText(/Article or event description/), {
      target: { value: "Test event" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Run Analysis" }));
    expect(
      screen.getByRole("button", { name: /Waiting for response/ }),
    ).toBeDisabled();
    reject(new Error("Checkpoint missing"));
    expect(await screen.findByText("Checkpoint missing")).toBeInTheDocument();
    expect(useAnalysisStore.getState().history).toHaveLength(0);
    expect(screen.getByRole("button", { name: "Run Analysis" })).toBeEnabled();
  });
  it("can retry failed health requests and keeps unknown states honest", async () => {
    vi.mocked(apiClient.getHealth).mockRejectedValueOnce(new Error("Offline"));
    render(<App />);
    expect(await screen.findByText("Offline")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    await screen.findByText(/SYNTHETIC execution/);
    expect(screen.queryByText("Offline")).toBeNull();
  });
  it("submits standalone research and renders returned queries", async () => {
    vi.mocked(apiClient.research).mockResolvedValue(research);
    window.history.replaceState({}, "", "/research");
    render(<App />);
    fillDates();
    fireEvent.change(screen.getByLabelText(/Article or event description/), {
      target: { value: "Research this event" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Run Research" }));
    expect(await screen.findByText("test query")).toBeInTheDocument();
    expect(apiClient.research).toHaveBeenCalledWith(
      expect.objectContaining({ live_research: true }),
    );
  });
  it("calls only supported historical filters and shows empty results", async () => {
    vi.mocked(apiClient.historicalSearch).mockResolvedValue({
      analogues: [],
      similarity_components: {},
      historical_outcomes: [],
      retrieval_metadata: {},
      temporal_safety_status: "VERIFIED",
    });
    window.history.replaceState({}, "", "/historical");
    render(<App />);
    fireEvent.change(screen.getByLabelText("Event text"), {
      target: { value: "Historical query" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Search Historical Events" }),
    );
    await waitFor(() =>
      expect(apiClient.historicalSearch).toHaveBeenCalledWith(
        expect.objectContaining({ text: "Historical query", top_k: 5 }),
      ),
    );
    expect(screen.getByText(/empty placeholder/)).toBeInTheDocument();
    expect(
      screen.getByText("No historical analogues returned"),
    ).toBeInTheDocument();
  });
  it("requires simulation acknowledgment and renders returned backtest metrics with labels", async () => {
    vi.mocked(apiClient.startBacktest).mockResolvedValue({
      run_id: "test-backtest",
      status: "COMPLETED",
      metrics: { accuracy: 0.85 },
    });
    window.history.replaceState({}, "", "/backtests");
    render(<App />);
    expect(
      screen.getByRole("button", { name: "Start Simulation Run" }),
    ).toBeDisabled();
    fireEvent.click(screen.getByLabelText(/I understand this run/));
    fireEvent.click(
      screen.getByRole("button", { name: "Start Simulation Run" }),
    );
    expect(
      await screen.findByText("Returned simulated metrics"),
    ).toBeInTheDocument();
    expect(apiClient.startBacktest).toHaveBeenCalledWith({
      domain: "geopolitics",
      window_days: 7,
    });
  });
});
