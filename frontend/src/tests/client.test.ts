import { afterEach, describe, expect, it, vi } from "vitest";
import { APIClient, DelphiAPIError } from "../api/client";
import { parseGraph } from "../utils/graph";
import { safeUrl } from "../utils/presentation";
import { validateTemporal } from "../utils/validation";
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});
describe("API boundaries", () => {
  it("uses configured endpoints and preserves idempotency header and integer horizon", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetch);
    const request = {
      text: "test",
      domain: "security",
      publication_timestamp: "2026-01-01",
      prediction_information_cutoff: "2026-01-02",
      forecast_horizon: 90,
    };
    await new APIClient("https://api.example.com/").analyze(
      request,
      "test-key",
    );
    expect(fetch).toHaveBeenCalledWith(
      "https://api.example.com/analysis",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(request),
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": "test-key",
        },
      }),
    );
  });
  it("normalizes FastAPI validation errors instead of reporting false success", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(
            JSON.stringify({ detail: [{ msg: "Field required" }] }),
            { status: 422 },
          ),
        ),
    );
    await expect(new APIClient().getHealth()).rejects.toThrow("Field required");
  });
  it("keeps structured backend failures", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(
            JSON.stringify({
              error_code: "MODEL_MISSING",
              message: "Missing artifact",
              request_id: "test-request",
            }),
            { status: 500 },
          ),
        ),
    );
    try {
      await new APIClient().getModels();
      throw new Error("Expected failure");
    } catch (e) {
      expect(e).toBeInstanceOf(DelphiAPIError);
      expect((e as DelphiAPIError).apiError.request_id).toBe("test-request");
    }
  });
  it("does not invent causal edges from a forecast trajectory", () => {
    expect(
      parseGraph({ event_id: "test", trajectory: [{ event_type: 1 }] }),
    ).toBeNull();
    expect(
      parseGraph({
        causal_graph: {
          nodes: [{ id: "a", label: "A", kind: "observed" }],
          edges: [
            { id: "e", source: "a", target: "missing", kind: "inferred" },
          ],
        },
      }),
    ).toBeNull();
  });
  it("rejects executable source URLs and invalid or leaking temporal bounds", () => {
    expect(safeUrl("javascript:alert(1)")).toBeNull();
    expect(safeUrl("https://example.com")).toBe("https://example.com/");
    expect(validateTemporal("invalid", "2026-01-01")).toContain("valid");
    expect(validateTemporal("2026-02-01", "2026-01-01")).toContain(
      "TEMPORAL LEAKAGE",
    );
  });
});
