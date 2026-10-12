export function validateTemporal(
  publicationDate: string,
  cutoffDate: string,
): string | null {
  if (!publicationDate || !cutoffDate)
    return "Publication date and prediction cutoff are required.";
  const pub = new Date(publicationDate).getTime(),
    cutoff = new Date(cutoffDate).getTime();
  if (!Number.isFinite(pub) || !Number.isFinite(cutoff))
    return "Enter valid publication and cutoff dates.";
  if (pub > cutoff)
    return "Publication timestamp cannot be after prediction cutoff (TEMPORAL LEAKAGE).";
  return null;
}
export function localDateTime() {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}
