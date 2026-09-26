export function formatTimestamp(ts: string): string {
    return new Date(ts).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  export function formatPercent(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }
  
  export function mapEventType(type: number): string {
    const types: Record<number, string> = {
      1: "Protest",
      2: "Sanction",
      3: "Military Mobilization",
      4: "Policy Change",
      5: "Election",
      6: "Diplomatic Talk"
    };
    return types[type] || `Unknown (${type})`;
  }
  
  export function mapActor(actorId?: number): string {
    return actorId ? `Actor ${actorId}` : "None";
  }
  
  export function mapDomain(domainId?: number): string {
    const domains: Record<number, string> = {
      1: "Geopolitics",
      2: "Economics",
      3: "Security"
    };
    return domainId ? (domains[domainId] || `Domain ${domainId}`) : "Unknown";
  }
