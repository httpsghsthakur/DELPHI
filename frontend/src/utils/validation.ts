export function validateTemporal(publicationDate: string, cutoffDate: string): string | null {
    if (!publicationDate || !cutoffDate) return null;
    
    const pub = new Date(publicationDate).getTime();
    const cutoff = new Date(cutoffDate).getTime();
    
    if (pub > cutoff) {
      return "Publication timestamp cannot be after prediction cutoff (TEMPORAL LEAKAGE).";
    }
    return null;
  }
