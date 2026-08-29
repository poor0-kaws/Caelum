import { sampleDashboard } from "../data/sampleDashboard";
import type { DashboardData, DataMode } from "../types";


export async function getDashboard(
  mode: DataMode,
  signal?: AbortSignal,
): Promise<DashboardData> {
  if (mode === "sample") {
    return sampleDashboard;
  }

  const response = await fetch(`/api/dashboard?mode=${mode}`, { signal });

  if (!response.ok) {
    throw new Error("Live data is unavailable. Switch back to sample data and try again later.");
  }

  return response.json() as Promise<DashboardData>;
}
