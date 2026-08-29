import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    kalshi_base_url: str = "https://external-api.kalshi.com/trade-api/v2"
    kalshi_series: str = "KXHIGHNY"
    latitude: float = 40.785091
    longitude: float = -73.968285
    station_id: str = "KNYC"
    request_timeout_seconds: float = 12.0
    user_agent: str = "kalshi-weather-dashboard/1.0 (local educational project)"
    minimum_calibration_days: int = 30
    history_path: Path = Path(__file__).resolve().parents[1] / "data" / "knyc_forecast_history.json"


def load_settings() -> Settings:
    """Read optional settings without requiring trading credentials."""
    return Settings(
        kalshi_base_url=os.getenv(
            "KALSHI_BASE_URL",
            "https://external-api.kalshi.com/trade-api/v2",
        ),
        kalshi_series=os.getenv("KALSHI_SERIES", "KXHIGHNY"),
        user_agent=os.getenv(
            "NWS_USER_AGENT",
            "kalshi-weather-dashboard/1.0 (local educational project)",
        ),
        minimum_calibration_days=int(os.getenv("MINIMUM_CALIBRATION_DAYS", "30")),
    )
