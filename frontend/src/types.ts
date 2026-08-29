export type DataMode = "sample" | "live";

export interface HourlyTemperature {
  time: string;
  temperature: number;
  kind: "observed" | "forecast";
}

export interface WeatherSnapshot {
  location: string;
  station: string;
  observed_high: number | null;
  observed_low: number | null;
  forecast_high: number;
  projected_high: number;
  condition: string;
  hourly: HourlyTemperature[];
}

export interface Recommendation {
  ticker: string;
  range_label: string;
  action: "BUY YES" | "BUY NO" | "WAIT";
  confidence: number;
  edge: number;
  reasoning: string;
}

export interface ScoredMarket {
  ticker: string;
  title: string;
  range_label: string;
  yes_bid: number;
  yes_ask: number;
  no_ask: number;
  model_probability: number;
  edge: number;
  volume: number;
  status: string;
}

export interface DashboardData {
  source: DataMode;
  generated_at: string;
  notice: string;
  weather: WeatherSnapshot;
  recommendation: Recommendation;
  markets: ScoredMarket[];
}
