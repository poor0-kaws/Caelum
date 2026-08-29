export function formatCents(value: number): string {
  return `${Math.round(value * 100)}¢`;
}


export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}


export function formatEdge(value: number): string {
  const cents = Math.round(value * 100);
  const sign = cents > 0 ? "+" : "";
  return `${sign}${cents}¢`;
}


export function formatVolume(value: number): string {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
}


export function formatRefreshTime(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown time";
  }

  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}
