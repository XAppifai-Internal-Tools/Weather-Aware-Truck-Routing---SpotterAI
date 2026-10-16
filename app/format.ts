export const RISK_LABELS = ["Low", "Moderate", "High", "Severe", "No Travel"];
export const RISK_COLORS = ["#16a34a", "#eab308", "#f97316", "#dc2626", "#7e22ce"];
export const ROUTE_COLORS = ["#2563eb", "#0891b2", "#db2777"];

export function formatHours(hours: number) {
  const minutes = Math.round(hours * 60);
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export function formatTime(iso: string) {
  return new Date(iso).toLocaleString([], { weekday: "short", hour: "numeric", minute: "2-digit" });
}
