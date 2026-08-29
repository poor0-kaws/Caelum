from datetime import datetime
from typing import Any

from app.clients.http import JsonHttpClient
from app.config import Settings
from app.models import HourlyTemperature, WeatherSnapshot


class NwsClient:
    """Read NYC observations and forecasts from the National Weather Service."""

    def __init__(self, settings: Settings, http: JsonHttpClient) -> None:
        self.settings = settings
        self.http = http

    def get_weather(self) -> WeatherSnapshot:
        point = self._get_point_metadata()
        forecast_url = point["properties"]["forecast"]
        hourly_url = point["properties"]["forecastHourly"]

        observations = self._get_today_observations()
        forecast = self.http.get(forecast_url)
        hourly_forecast = self.http.get(hourly_url)

        observed_temperatures = [item.temperature for item in observations]
        observed_high = max(observed_temperatures, default=None)
        observed_low = min(observed_temperatures, default=None)

        forecast_high, condition = self._read_daytime_forecast(forecast)
        projected_high = max(observed_high or forecast_high, forecast_high)
        timeline = self._merge_timeline(observations, hourly_forecast)

        return WeatherSnapshot(
            location="New York City",
            station=self.settings.station_id,
            observed_high=observed_high,
            observed_low=observed_low,
            forecast_high=forecast_high,
            projected_high=projected_high,
            condition=condition,
            hourly=timeline,
        )

    def _get_point_metadata(self) -> dict[str, Any]:
        url = (
            "https://api.weather.gov/points/"
            f"{self.settings.latitude},{self.settings.longitude}"
        )
        return self.http.get(url)

    def _get_today_observations(self) -> list[HourlyTemperature]:
        url = (
            "https://api.weather.gov/stations/"
            f"{self.settings.station_id}/observations"
        )
        data = self.http.get(url, params={"limit": 48})
        today = datetime.now().astimezone().date()
        observations: list[HourlyTemperature] = []

        for feature in data.get("features", []):
            properties = feature.get("properties", {})
            timestamp = _parse_time(properties.get("timestamp"))
            celsius = properties.get("temperature", {}).get("value")

            if timestamp is None or celsius is None:
                continue

            local_time = timestamp.astimezone()
            if local_time.date() != today:
                continue

            observations.append(
                HourlyTemperature(
                    time=local_time.strftime("%I %p").lstrip("0"),
                    temperature=_celsius_to_fahrenheit(float(celsius)),
                    kind="observed",
                )
            )

        observations.sort(key=lambda item: _hour_sort_value(item.time))
        return observations

    def _read_daytime_forecast(self, data: dict[str, Any]) -> tuple[int, str]:
        periods = data.get("properties", {}).get("periods", [])

        for period in periods:
            if period.get("isDaytime"):
                return int(period.get("temperature", 0)), period.get("shortForecast", "")

        return 0, "Forecast unavailable"

    def _merge_timeline(
        self,
        observations: list[HourlyTemperature],
        hourly_data: dict[str, Any],
    ) -> list[HourlyTemperature]:
        timeline = observations[-6:]
        seen_times = {item.time for item in timeline}
        today = datetime.now().astimezone().date()

        for period in hourly_data.get("properties", {}).get("periods", []):
            timestamp = _parse_time(period.get("startTime"))
            if timestamp is None:
                continue

            local_time = timestamp.astimezone()
            if local_time.date() != today:
                continue

            label = local_time.strftime("%I %p").lstrip("0")
            if label in seen_times:
                continue

            timeline.append(
                HourlyTemperature(
                    time=label,
                    temperature=int(period.get("temperature", 0)),
                    kind="forecast",
                )
            )
            seen_times.add(label)

            if len(timeline) >= 12:
                break

        return timeline


def _celsius_to_fahrenheit(celsius: float) -> int:
    return round((celsius * 9 / 5) + 32)


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _hour_sort_value(label: str) -> datetime:
    return datetime.strptime(label, "%I %p")
