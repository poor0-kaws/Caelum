import { Info, TrendUp } from "@phosphor-icons/react";

import { formatEdge } from "../lib/format";
import type { ModelSummary, Recommendation } from "../types";


interface RecommendationPanelProps {
  recommendation: Recommendation;
  model: ModelSummary;
}


export function RecommendationPanel({
  recommendation,
  model,
}: RecommendationPanelProps) {
  const actionClass = recommendation.action === "WAIT" ? "wait" : "trade";

  return (
    <section className="recommendation-panel" aria-labelledby="recommendation-title">
      <div className="section-heading-row">
        <div>
          <p className="section-kicker">Best modeled setup</p>
          <h2 id="recommendation-title">{recommendation.range_label}</h2>
        </div>
        <div className={`action-badge ${actionClass}`}>
          <TrendUp size={17} weight="bold" />
          {recommendation.action}
        </div>
      </div>

      <div className="recommendation-metrics">
        <div>
          <span>Modeled edge</span>
          <strong>{formatEdge(recommendation.edge)}</strong>
        </div>
        <div>
          <span>Signal confidence</span>
          <strong>{recommendation.confidence}%</strong>
        </div>
      </div>

      <p className="recommendation-reasoning">{recommendation.reasoning}</p>

      <div className="model-note">
        <Info size={16} weight="fill" />
        <span>{modelDescription(model)}</span>
      </div>
    </section>
  );
}


function modelDescription(model: ModelSummary): string {
  if (model.source === "knyc_error_history") {
    return `Uses ${model.completed_days} completed KNYC forecast-error days.`;
  }

  return (
    `Uses NOAA NBM percentiles while KNYC calibration builds `
    + `(${model.completed_days}/${model.required_days} completed days).`
  );
}
