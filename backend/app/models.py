from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class HourlyTemperature:
    time: str
    temperature: int
    kind: str


@dataclass(frozen=True)
class WeatherSnapshot:
    location: str
    station: str
    observed_high: int | None
    observed_low: int | None
    forecast_high: int
    projected_high: int
    condition: str
    hourly: list[HourlyTemperature] = field(default_factory=list)


@dataclass(frozen=True)
class Market:
    ticker: str
    title: str
    range_label: str
    minimum_temperature: int | None
    maximum_temperature: int | None
    yes_bid: float
    yes_ask: float
    no_ask: float
    volume: float
    status: str


@dataclass(frozen=True)
class ScoredMarket:
    ticker: str
    title: str
    range_label: str
    yes_bid: float
    yes_ask: float
    no_ask: float
    model_probability: float
    edge: float
    volume: float
    status: str


@dataclass(frozen=True)
class Recommendation:
    ticker: str
    range_label: str
    action: str
    confidence: int
    edge: float
    reasoning: str


@dataclass(frozen=True)
class ModelSummary:
    source: str
    label: str
    completed_days: int
    required_days: int
    as_of: str


@dataclass(frozen=True)
class DashboardData:
    source: str
    generated_at: datetime
    notice: str
    weather: WeatherSnapshot
    model: ModelSummary
    recommendation: Recommendation
    markets: list[ScoredMarket]
