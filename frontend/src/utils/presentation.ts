export const humanize = (s: string) =>
  s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
export const display = (value: unknown): string =>
  value === undefined || value === null || value === ""
    ? "Not reported"
    : typeof value === "object"
      ? JSON.stringify(value)
      : String(value);
export const safeUrl = (value: unknown): string | null => {
  if (typeof value !== "string") return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
};
