import { useCallback, useEffect, useState } from "react";
import { WarningCircle } from "@phosphor-icons/react";

import { ForecastChart } from "./components/ForecastChart";
import { LoadingDashboard } from "./components/LoadingDashboard";
import { MarketTable } from "./components/MarketTable";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { TopBar } from "./components/TopBar";
import { getDashboard } from "./lib/dashboardApi";
import { formatRefreshTime } from "./lib/format";
import type { DashboardData } from "./types";


function App() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  const loadDashboard = useCallback(async (signal?: AbortSignal) => {
    setIsLoading(true);
    setError(null);

    try {
      const nextDashboard = await getDashboard(signal);
      setDashboard(nextDashboard);
    } catch (requestError) {
      if (requestError instanceof DOMException && requestError.name === "AbortError") {
        return;
      }

      const message = requestError instanceof Error
        ? requestError.message
        : "The dashboard could not be loaded.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void loadDashboard(controller.signal);
    return () => controller.abort();
  }, [loadDashboard, refreshKey]);

  function refresh() {
    setRefreshKey((current) => current + 1);
  }

  return (
    <div className="app-frame">
      <TopBar
        isLoading={isLoading}
        onRefresh={refresh}
      />

      {isLoading && !dashboard ? <LoadingDashboard /> : null}

      {error && !dashboard ? (
        <main className="dashboard-shell">
          <div className="error-banner" role="alert">
            <WarningCircle size={19} weight="fill" />
            <span>{error}</span>
            <button type="button" onClick={refresh}>Retry live data</button>
          </div>
        </main>
      ) : null}

      {dashboard ? (
        <main className="dashboard-shell">
          {error ? (
            <div className="error-banner" role="alert">
              <WarningCircle size={19} weight="fill" />
              <span>{error}</span>
              <button type="button" onClick={refresh}>Retry live data</button>
            </div>
          ) : null}

          <section className="overview-strip" aria-label="Weather summary">
            <div className="primary-temperature">
              <span>Projected high</span>
              <strong>{dashboard.weather.projected_high}°</strong>
              <p>{dashboard.weather.condition}</p>
            </div>

            <div className="overview-metric">
              <span>Observed high</span>
              <strong>
                {dashboard.weather.observed_high === null
                  ? "Pending"
                  : `${dashboard.weather.observed_high}°F`}
              </strong>
              <p>
                {dashboard.weather.observed_high === null
                  ? "No reading received today"
                  : `Central Park, ${dashboard.weather.station}`}
              </p>
            </div>

            <div className="overview-metric">
              <span>NWS forecast</span>
              <strong>{dashboard.weather.forecast_high}°F</strong>
              <p>Daily maximum</p>
            </div>

            <div className="overview-metric status-metric">
              <span>Data source</span>
              <strong><i className="status-dot" />{dashboard.source}</strong>
              <p>Updated {formatRefreshTime(dashboard.generated_at)}</p>
            </div>
          </section>

          <div className="content-grid">
            <section className="forecast-panel" aria-labelledby="forecast-title">
              <div className="panel-heading">
                <div>
                  <h2 id="forecast-title">Today’s temperature path</h2>
                  <p>Observed readings continue into the NWS hourly forecast.</p>
                </div>
                <span>°F</span>
              </div>
              <ForecastChart points={dashboard.weather.hourly} />
            </section>

            <RecommendationPanel
              recommendation={dashboard.recommendation}
              model={dashboard.model}
            />
          </div>

          <section className="markets-panel" aria-labelledby="markets-title">
            <div className="panel-heading market-heading">
              <div>
                <h2 id="markets-title">Open contracts</h2>
                <p>Sorted by the model’s estimated edge over the current YES ask.</p>
              </div>
              <span>{dashboard.markets.length} markets</span>
            </div>
            <MarketTable markets={dashboard.markets} />
          </section>

          <footer className="dashboard-footer">
            <p>{dashboard.notice}</p>
            <p>Weather: NWS and KNYC. Probability: NOAA NBM. Prices: Kalshi.</p>
          </footer>
        </main>
      ) : null}
    </div>
  );
}


export default App;
