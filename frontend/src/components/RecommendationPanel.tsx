import { Info, TrendUp } from "@phosphor-icons/react";

import { formatEdge } from "../lib/format";
import type { Recommendation } from "../types";


interface RecommendationPanelProps {
  recommendation: Recommendation;
}


export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
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
        <span>Uses a simple normal distribution with 2.25°F forecast uncertainty.</span>
      </div>
    </section>
  );
}
