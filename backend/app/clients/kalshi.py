import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.clients.http import JsonHttpClient
from app.config import Settings
from app.models import Market


class KalshiClient:
    """Read public NYC high-temperature markets. This client cannot place orders."""

    def __init__(self, settings: Settings, http: JsonHttpClient) -> None:
        self.settings = settings
        self.http = http

    def get_open_markets(self) -> list[Market]:
        url = f"{self.settings.kalshi_base_url}/markets"
        data = self.http.get(
            url,
            params={
                "series_ticker": self.settings.kalshi_series,
                "status": "open",
                "limit": 100,
            },
        )

        event_date = datetime.now(ZoneInfo("America/New_York")).strftime("%y%b%d").upper()
        today_items = [
            item
            for item in data.get("markets", [])
            if event_date in str(item.get("ticker", ""))
        ]
        markets = [parse_market(item) for item in today_items]
        valid_markets = [market for market in markets if market is not None]
        return sorted(valid_markets, key=_market_sort_key)


def parse_market(data: dict[str, Any]) -> Market | None:
    """Turn one provider response into the app's simple market shape."""
    ticker = str(data.get("ticker", "")).strip()
    title = str(data.get("title", "")).strip()
    yes_sub_title = str(data.get("yes_sub_title", "")).strip()

    if not ticker or not title:
        return None

    range_text = yes_sub_title or title
    minimum, maximum = _read_temperature_range(data, range_text)

    return Market(
        ticker=ticker,
        title=title,
        range_label=_format_range(minimum, maximum, range_text),
        minimum_temperature=minimum,
        maximum_temperature=maximum,
        yes_bid=_read_decimal(data, "yes_bid_dollars"),
        yes_ask=_read_decimal(data, "yes_ask_dollars"),
        no_ask=_read_decimal(data, "no_ask_dollars"),
        volume=_read_decimal(data, "volume_fp"),
        status=str(data.get("status", "open")),
    )


def _read_temperature_range(
    data: dict[str, Any],
    range_text: str,
) -> tuple[int | None, int | None]:
    text_numbers = [
        int(float(value))
        for value in re.findall(r"-?\d+(?:\.\d+)?", range_text)
    ]
    lowercase_text = range_text.lower()

    if len(text_numbers) >= 2:
        return text_numbers[0], text_numbers[1]

    if len(text_numbers) == 1 and "above" in lowercase_text:
        return text_numbers[0], None

    if len(text_numbers) == 1 and "below" in lowercase_text:
        return None, text_numbers[0]

    floor = _read_optional_number(data.get("floor_strike"))
    cap = _read_optional_number(data.get("cap_strike"))

    if floor is not None or cap is not None:
        return floor, cap

    numbers = [int(float(value)) for value in re.findall(r"-?\d+(?:\.\d+)?", range_text)]
    plausible = [value for value in numbers if -50 <= value <= 150]

    if len(plausible) >= 2:
        return plausible[-2], plausible[-1]

    if len(plausible) == 1 and "above" in lowercase_text:
        return plausible[0], None

    if len(plausible) == 1 and "below" in lowercase_text:
        return None, plausible[0]

    return None, None


def _read_optional_number(value: Any) -> int | None:
    if value is None or value == "":
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _read_decimal(data: dict[str, Any], key: str) -> float:
    try:
        return float(data.get(key, 0))
    except (TypeError, ValueError):
        return 0.0


def _format_range(
    minimum: int | None,
    maximum: int | None,
    fallback: str,
) -> str:
    if minimum is not None and maximum is not None:
        return f"{minimum}-{maximum}°F"

    if minimum is not None:
        return f"{minimum}°F or above"

    if maximum is not None:
        return f"{maximum}°F or below"

    return fallback


def _market_sort_key(market: Market) -> tuple[int, int]:
    minimum = market.minimum_temperature
    maximum = market.maximum_temperature
    return (minimum if minimum is not None else -999, maximum if maximum is not None else 999)
