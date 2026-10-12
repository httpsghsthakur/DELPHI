import type { JsonObject, ResearchReport } from "../api/types";
export function researchEvidence(report?: ResearchReport | null): JsonObject[] {
  return [
    ...(report?.supporting_evidence || []),
    ...(report?.conflicting_evidence || []),
  ].map((e) => ({ ...e }));
}

// The report and research payload can contain the same evidence item.
export function uniqueEvidence(items: JsonObject[]): JsonObject[] {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key =
      typeof item.evidence_id === "string"
        ? item.evidence_id
        : JSON.stringify(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
