from math import erf, sqrt

from app.models import Market, Recommendation, ScoredMarket


MINIMUM_EDGE = 0.03
FORECAST_UNCERTAINTY_DEGREES = 2.25


def score_markets(
    markets: list[Market],
    projected_high: int,
) -> tuple[list[ScoredMarket], Recommendation]:
    scored = [_score_market(market, projected_high) for market in markets]
    scored.sort(key=lambda market: market.edge, reverse=True)

    if not scored:
        return [], _empty_recommendation()

    best = scored[0]
    action = "BUY YES" if best.edge >= MINIMUM_EDGE else "WAIT"
    confidence = _confidence_from_edge(best.edge)
    reasoning = _build_reasoning(best, projected_high, action)

    recommendation = Recommendation(
        ticker=best.ticker,
        range_label=best.range_label,
        action=action,
        confidence=confidence,
        edge=best.edge,
        reasoning=reasoning,
    )
    return scored, recommendation


def _score_market(market: Market, projected_high: int) -> ScoredMarket:
    probability = _range_probability(
        projected_high,
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


def _range_probability(
    projected_high: int,
    minimum: int | None,
    maximum: int | None,
) -> float:
    if minimum is None and maximum is None:
        return 0.0

    lower = float("-inf") if minimum is None else minimum - 0.5
    upper = float("inf") if maximum is None else maximum + 0.5
    upper_probability = _normal_cdf(upper, projected_high, FORECAST_UNCERTAINTY_DEGREES)
    lower_probability = _normal_cdf(lower, projected_high, FORECAST_UNCERTAINTY_DEGREES)
    return max(0.0, min(1.0, upper_probability - lower_probability))


def _normal_cdf(value: float, mean: float, standard_deviation: float) -> float:
    if value == float("inf"):
        return 1.0

    if value == float("-inf"):
        return 0.0

    z_score = (value - mean) / (standard_deviation * sqrt(2))
    return 0.5 * (1 + erf(z_score))


def _confidence_from_edge(edge: float) -> int:
    bounded_edge = max(0.0, min(edge, 0.25))
    return round(50 + (bounded_edge / 0.25) * 40)


def _build_reasoning(
    market: ScoredMarket,
    projected_high: int,
    action: str,
) -> str:
    model_percent = round(market.model_probability * 100)
    ask_percent = round(market.yes_ask * 100)

    if action == "WAIT":
        return (
            f"The strongest contract is {market.range_label}, but its modeled edge is below "
            f"the {round(MINIMUM_EDGE * 100)} cent watch threshold. The projected high is "
            f"{projected_high}°F. Waiting avoids forcing a weak trade."
        )

    return (
        f"The projected high is {projected_high}°F. The simple weather model estimates a "
        f"{model_percent}% chance for {market.range_label}, compared with a {ask_percent} cent "
        "YES ask. This is an educational signal, not a calibrated trading model."
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
