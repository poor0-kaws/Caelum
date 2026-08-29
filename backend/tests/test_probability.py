import unittest
from datetime import date, datetime, timezone

from app.clients.nbm import NbmTemperatureGuidance
from app.services.probability import (
    EmpiricalErrorModel,
    QuantileTemperatureModel,
    choose_probability_model,
)


class ProbabilityModelTests(unittest.TestCase):
    def test_quantile_model_assigns_more_probability_near_the_median(self) -> None:
        model = QuantileTemperatureModel(
            percentiles={10: 76, 25: 78, 50: 80, 75: 82, 90: 84},
            observed_floor=None,
        )

        center = model.range_probability(79, 81)
        tail = model.range_probability(86, None)

        self.assertGreater(center, tail)

    def test_observed_high_removes_impossible_lower_outcomes(self) -> None:
        model = QuantileTemperatureModel(
            percentiles={10: 76, 25: 78, 50: 80, 75: 82, 90: 84},
            observed_floor=81,
        )

        self.assertEqual(model.range_probability(None, 80), 0.0)
        self.assertAlmostEqual(model.range_probability(81, None), 1.0)

    def test_empirical_model_uses_real_error_counts(self) -> None:
        model = EmpiricalErrorModel(
            forecast_high=80,
            historical_errors=[-2, -1, 0, 0, 1, 2],
            observed_floor=None,
        )

        probability = model.range_probability(80, 80)

        self.assertAlmostEqual(probability, 2 / 6)

    def test_local_history_takes_over_after_minimum_sample(self) -> None:
        guidance = NbmTemperatureGuidance(
            target_date=date(2026, 8, 29),
            issued_at=datetime(2026, 8, 29, 1, tzinfo=timezone.utc),
            percentiles={10: 76, 25: 78, 50: 80, 75: 82, 90: 84},
        )

        model, summary = choose_probability_model(
            guidance=guidance,
            historical_errors=[0] * 30,
            observed_high=None,
            minimum_calibration_days=30,
        )

        self.assertIsInstance(model, EmpiricalErrorModel)
        self.assertEqual(summary.source, "knyc_error_history")
        self.assertEqual(summary.completed_days, 30)


if __name__ == "__main__":
    unittest.main()
