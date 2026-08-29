from datetime import datetime

from app.models import HourlyTemperature, Market, WeatherSnapshot


def sample_weather() -> WeatherSnapshot:
    return WeatherSnapshot(
        location="New York City",
        station="KNYC",
        observed_high=71,
        observed_low=64,
        forecast_high=74,
        projected_high=74,
        condition="Partly cloudy",
        hourly=[
            HourlyTemperature("8 AM", 65, "observed"),
            HourlyTemperature("9 AM", 67, "observed"),
            HourlyTemperature("10 AM", 69, "observed"),
            HourlyTemperature("11 AM", 71, "observed"),
            HourlyTemperature("12 PM", 72, "forecast"),
            HourlyTemperature("1 PM", 73, "forecast"),
            HourlyTemperature("2 PM", 74, "forecast"),
            HourlyTemperature("3 PM", 74, "forecast"),
            HourlyTemperature("4 PM", 73, "forecast"),
            HourlyTemperature("5 PM", 72, "forecast"),
        ],
    )


def sample_markets() -> list[Market]:
    values = [
        ("KXHIGHNY-SAMPLE-B70", "69°F or below", None, 69, 0.05, 0.07, 0.95, 288),
        ("KXHIGHNY-SAMPLE-B72", "70-72°F", 70, 72, 0.16, 0.18, 0.84, 613),
        ("KXHIGHNY-SAMPLE-B74", "73-75°F", 73, 75, 0.28, 0.30, 0.72, 1248),
        ("KXHIGHNY-SAMPLE-B77", "76-78°F", 76, 78, 0.19, 0.23, 0.80, 851),
        ("KXHIGHNY-SAMPLE-T79", "79°F or above", 79, None, 0.28, 0.30, 0.72, 340),
    ]

    return [
        Market(
            ticker=ticker,
            title=f"NYC high temperature: {label}",
            range_label=label,
            minimum_temperature=minimum,
            maximum_temperature=maximum,
            yes_bid=yes_bid,
            yes_ask=yes_ask,
            no_ask=no_ask,
            volume=volume,
            status="open",
        )
        for ticker, label, minimum, maximum, yes_bid, yes_ask, no_ask, volume in values
    ]
