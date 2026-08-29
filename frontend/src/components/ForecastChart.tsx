import type { HourlyTemperature } from "../types";


interface ForecastChartProps {
  points: HourlyTemperature[];
}


const WIDTH = 760;
const HEIGHT = 220;
const PADDING_X = 28;
const PADDING_Y = 28;


export function ForecastChart({ points }: ForecastChartProps) {
  if (points.length === 0) {
    return (
      <div className="empty-chart">
        <p>No hourly temperatures are available yet.</p>
      </div>
    );
  }

  const temperatures = points.map((point) => point.temperature);
  const minimum = Math.min(...temperatures) - 2;
  const maximum = Math.max(...temperatures) + 2;
  const drawableWidth = WIDTH - PADDING_X * 2;
  const drawableHeight = HEIGHT - PADDING_Y * 2;

  const chartPoints = points.map((point, index) => {
    const x = PADDING_X + (index / Math.max(points.length - 1, 1)) * drawableWidth;
    const percentFromTop = (maximum - point.temperature) / Math.max(maximum - minimum, 1);
    const y = PADDING_Y + percentFromTop * drawableHeight;
    return { ...point, x, y };
  });

  const observedLine = chartPoints
    .filter((point) => point.kind === "observed")
    .map((point) => `${point.x},${point.y}`)
    .join(" ");
  const forecastStart = Math.max(
    chartPoints.findIndex((point) => point.kind === "forecast") - 1,
    0,
  );
  const forecastLine = chartPoints
    .slice(forecastStart)
    .map((point) => `${point.x},${point.y}`)
    .join(" ");

  return (
    <div className="chart-wrap">
      <svg
        className="temperature-chart"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label="Observed and forecast hourly temperatures"
      >
        <line className="chart-grid" x1="28" y1="48" x2="732" y2="48" />
        <line className="chart-grid" x1="28" y1="110" x2="732" y2="110" />
        <line className="chart-grid" x1="28" y1="172" x2="732" y2="172" />

        {observedLine && <polyline className="observed-line" points={observedLine} />}
        {forecastLine && <polyline className="forecast-line" points={forecastLine} />}

        {chartPoints.map((point) => (
          <g key={`${point.time}-${point.kind}`}>
            <circle
              className={point.kind === "observed" ? "observed-point" : "forecast-point"}
              cx={point.x}
              cy={point.y}
              r="4"
            />
            <text className="chart-value" x={point.x} y={point.y - 12} textAnchor="middle">
              {point.temperature}°
            </text>
            <text className="chart-label" x={point.x} y={HEIGHT - 5} textAnchor="middle">
              {point.time}
            </text>
          </g>
        ))}
      </svg>

      <div className="chart-legend" aria-hidden="true">
        <span><i className="legend-line observed" />Observed</span>
        <span><i className="legend-line forecast" />Forecast</span>
      </div>
    </div>
  );
}
