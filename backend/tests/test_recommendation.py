import unittest

from app.models import Market
from app.services.probability import EmpiricalErrorModel
from app.services.recommendation import score_markets


class RecommendationTests(unittest.TestCase):
    def test_best_range_is_ranked_first(self) -> None:
        markets = [
            _market("LOW", 68, 70, 0.25),
            _market("CENTER", 72, 74, 0.20),
            _market("HIGH", 77, 79, 0.20),
        ]

        scored, recommendation = score_markets(
            markets,
            _probability_model(),
            projected_high=73,
        )

        self.assertEqual(scored[0].ticker, "CENTER")
        self.assertEqual(recommendation.ticker, "CENTER")
        self.assertEqual(recommendation.action, "BUY YES")

    def test_waits_when_no_market_has_enough_edge(self) -> None:
        markets = [_market("FAIR", 72, 74, 1.00)]

        _, recommendation = score_markets(
            markets,
            _probability_model(),
            projected_high=73,
        )

        self.assertEqual(recommendation.action, "WAIT")

    def test_empty_market_list_is_safe(self) -> None:
        scored, recommendation = score_markets(
            [],
            _probability_model(),
            projected_high=73,
        )

        self.assertEqual(scored, [])
        self.assertEqual(recommendation.action, "WAIT")
        self.assertEqual(recommendation.confidence, 0)


def _market(ticker: str, minimum: int, maximum: int, yes_ask: float) -> Market:
    return Market(
        ticker=ticker,
        title=ticker,
        range_label=f"{minimum}-{maximum}°F",
        minimum_temperature=minimum,
        maximum_temperature=maximum,
        yes_bid=max(yes_ask - 0.02, 0),
        yes_ask=yes_ask,
        no_ask=1 - max(yes_ask - 0.02, 0),
        volume=100,
        status="open",
    )


def _probability_model() -> EmpiricalErrorModel:
    return EmpiricalErrorModel(
        forecast_high=73,
        historical_errors=[-1, 0, 1] * 10,
        observed_floor=None,
    )


if __name__ == "__main__":
    unittest.main()
