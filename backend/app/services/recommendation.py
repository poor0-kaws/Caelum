from app.models import Market, Recommendation, ScoredMarket
from app.services.probability import TemperatureProbabilityModel


MINIMUM_EDGE = 0.03


def score_markets(
    markets: list[Market],
    model: TemperatureProbabilityModel,
    projected_high: int,
) -> tuple[list[ScoredMarket], Recommendation]:
    scored = [_score_market(market, model) for market in markets]
    scored.sort(key=lambda market: market.edge, reverse=True)

    if not scored:
        return [], _empty_recommendation()

    best = scored[0]
    action = "BUY YES" if best.edge >= MINIMUM_EDGE else "WAIT"
    confidence = _confidence_from_edge(best.edge)
    reasoning = _build_reasoning(best, projected_high, action, model.label)

    recommendation = Recommendation(
        ticker=best.ticker,
        range_label=best.range_label,
        action=action,
        confidence=confidence,
        edge=best.edge,
        reasoning=reasoning,
    )
    return scored, recommendation


def _score_market(
    market: Market,
    model: TemperatureProbabilityModel,
) -> ScoredMarket:
    probability = model.range_probability(
        market.minimum_temperature,
        market.maximum_temperature,
    )
    edge = probability - market.yes_ask

    return ScoredMarket(
        ticker=market.ticker,
        title=market.title,
        range_label=market.range_label,
        yes_bid=market.yes_bid,
        yes_ask=market.yes_ask,
        no_ask=market.no_ask,
        model_probability=round(probability, 4),
        edge=round(edge, 4),
        volume=market.volume,
        status=market.status,
    )


def _confidence_from_edge(edge: float) -> int:
    bounded_edge = max(0.0, min(edge, 0.25))
    return round(50 + (bounded_edge / 0.25) * 40)


def _build_reasoning(
    market: ScoredMarket,
    projected_high: int,
    action: str,
    model_label: str,
) -> str:
    model_percent = round(market.model_probability * 100)
    ask_percent = round(market.yes_ask * 100)

    if action == "WAIT":
        return (
            f"The strongest contract is {market.range_label}, but its modeled edge is below "
            f"the {round(MINIMUM_EDGE * 100)} cent watch threshold. The projected high is "
            f"{projected_high}°F. {model_label} does not show a strong enough advantage."
        )

    return (
        f"The projected high is {projected_high}°F. The active probability model estimates a "
        f"{model_percent}% chance for {market.range_label}, compared with a {ask_percent} cent "
        f"YES ask. The probability source is {model_label}."
    )


def _empty_recommendation() -> Recommendation:
    return Recommendation(
        ticker="",
        range_label="No open market",
        action="WAIT",
        confidence=0,
        edge=0.0,
        reasoning="No open NYC high-temperature contracts were returned.",
    )
