from bisect import bisect_right
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

from app.clients.nbm import NbmTemperatureGuidance
from app.models import ModelSummary


class TemperatureProbabilityModel(Protocol):
    source: str
    label: str

    def range_probability(
        self,
        minimum: int | None,
        maximum: int | None,
    ) -> float:
        """Return the chance that the final high lands inside a market range."""


@dataclass(frozen=True)
class QuantileTemperatureModel:
    """A nonparametric distribution drawn through NOAA percentile points."""

    percentiles: dict[int, float]
    observed_floor: int | None
    source: str = "nbm_percentiles"
    label: str = "NOAA NBM calibrated percentiles"

    def range_probability(
        self,
        minimum: int | None,
        maximum: int | None,
    ) -> float:
        return _conditional_range_probability(
            cdf=self._cdf,
            minimum=minimum,
            maximum=maximum,
            observed_floor=self.observed_floor,
        )

    def _cdf(self, value: float) -> float:
        points = _quantile_points(self.percentiles)

        if value < points[0][0]:
            return 0.0

        for index in range(1, len(points)):
            previous_value, previous_probability = points[index - 1]
            current_value, current_probability = points[index]

            if value >= current_value:
                continue

            distance = current_value - previous_value
            if distance <= 0:
                return current_probability

            fraction = (value - previous_value) / distance
            return previous_probability + fraction * (
                current_probability - previous_probability
            )

        return 1.0


@dataclass(frozen=True)
class EmpiricalErrorModel:
    """A distribution made from real KNYC forecast errors, with no shape assumption."""

    forecast_high: float
    historical_errors: Sequence[float]
    observed_floor: int | None
    source: str = "knyc_error_history"
    label: str = "Calibrated KNYC forecast-error history"

    def range_probability(
        self,
        minimum: int | None,
        maximum: int | None,
    ) -> float:
        outcomes = sorted(
            self.forecast_high + error
            for error in self.historical_errors
        )

        return _conditional_range_probability(
            cdf=lambda value: _empirical_cdf(outcomes, value),
            minimum=minimum,
            maximum=maximum,
            observed_floor=self.observed_floor,
        )


def choose_probability_model(
    guidance: NbmTemperatureGuidance,
    historical_errors: Sequence[float],
    observed_high: int | None,
    minimum_calibration_days: int,
) -> tuple[TemperatureProbabilityModel, ModelSummary]:
    completed_days = len(historical_errors)

    if completed_days >= minimum_calibration_days:
        model = EmpiricalErrorModel(
            forecast_high=guidance.percentiles[50],
            historical_errors=historical_errors,
            observed_floor=observed_high,
        )
    else:
        model = QuantileTemperatureModel(
            percentiles=guidance.percentiles,
            observed_floor=observed_high,
        )

    summary = ModelSummary(
        source=model.source,
        label=model.label,
        completed_days=completed_days,
        required_days=minimum_calibration_days,
        as_of=guidance.issued_at.isoformat(),
    )
    return model, summary


def _quantile_points(percentiles: dict[int, float]) -> list[tuple[float, float]]:
    required = {10, 25, 50, 75, 90}
    if not required.issubset(percentiles):
        raise ValueError("Temperature percentiles must include 10, 25, 50, 75, and 90.")

    lower_tail = max(percentiles[25] - percentiles[10], 1.0) * 2
    upper_tail = max(percentiles[90] - percentiles[75], 1.0) * 2

    return [
        (percentiles[10] - lower_tail, 0.0),
        (percentiles[10], 0.10),
        (percentiles[25], 0.25),
        (percentiles[50], 0.50),
        (percentiles[75], 0.75),
        (percentiles[90], 0.90),
        (percentiles[90] + upper_tail, 1.0),
    ]


def _conditional_range_probability(
    *,
    cdf: Callable[[float], float],
    minimum: int | None,
    maximum: int | None,
    observed_floor: int | None,
) -> float:
    if minimum is None and maximum is None:
        return 0.0

    lower_boundary = float("-inf") if minimum is None else minimum - 0.5
    upper_boundary = float("inf") if maximum is None else maximum + 0.5

    if observed_floor is None:
        probability = cdf(upper_boundary) - cdf(lower_boundary)
        return _bounded(probability)

    floor_boundary = observed_floor - 0.5
    if upper_boundary <= floor_boundary:
        return 0.0

    possible_lower_boundary = max(lower_boundary, floor_boundary)
    remaining_probability = 1.0 - cdf(floor_boundary)

    if remaining_probability <= 0:
        return 1.0 if upper_boundary == float("inf") else 0.0

    probability = (
        cdf(upper_boundary) - cdf(possible_lower_boundary)
    ) / remaining_probability
    return _bounded(probability)


def _empirical_cdf(values: Sequence[float], value: float) -> float:
    if not values:
        return 0.0

    return bisect_right(values, value) / len(values)


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))
