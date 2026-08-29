import type { DashboardData } from "../types";


export async function getDashboard(
  signal?: AbortSignal,
): Promise<DashboardData> {
  const response = await fetch("/api/dashboard", { signal });

  if (!response.ok) {
    throw new Error(
      "Live data could not be loaded. The Python API or an outside data provider may be unavailable.",
    );
  }

  return response.json() as Promise<DashboardData>;
}
