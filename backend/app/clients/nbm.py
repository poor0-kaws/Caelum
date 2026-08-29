import re
from dataclasses import dataclass
from datetime import date, datetime, timezone

from app.clients.http import JsonHttpClient


PERCENTILE_ROWS = {
    "TXNP1": 10,
    "TXNP2": 25,
    "TXNP5": 50,
    "TXNP7": 75,
    "TXNP9": 90,
}


@dataclass(frozen=True)
class NbmTemperatureGuidance:
    target_date: date
    issued_at: datetime
    percentiles: dict[int, float]


class NbmClient:
    """Read KNYC maximum-temperature percentiles from NOAA's NBM bulletin."""

    def __init__(self, http: JsonHttpClient, station_id: str) -> None:
        self.http = http
        self.station_id = station_id

    def get_daily_maximum_guidance(self, target_date: date) -> NbmTemperatureGuidance:
        url = _bulletin_url(target_date)
        station_lines = _find_station_lines(
            self.http.iter_lines(url),
            self.station_id,
        )
        return parse_station_guidance(station_lines, target_date)


def parse_station_guidance(
    lines: list[str],
    target_date: date,
) -> NbmTemperatureGuidance:
    if not lines:
        raise ValueError("The KNYC station was not found in the NBM bulletin.")

    issued_at = _parse_issue_time(lines[0])
    percentiles: dict[int, float] = {}

    for line in lines:
        row_name = line[:6].strip()
        percentile = PERCENTILE_ROWS.get(row_name)

        if percentile is None:
            continue

        values = _read_row_values(line[6:])
        if not values:
            continue

        # The first maximum-temperature value ends at 00 UTC after the local day.
        percentiles[percentile] = float(values[0])

    if set(percentiles) != set(PERCENTILE_ROWS.values()):
        raise ValueError("The NBM bulletin is missing maximum-temperature percentiles.")

    return NbmTemperatureGuidance(
        target_date=target_date,
        issued_at=issued_at,
        percentiles=percentiles,
    )


def _bulletin_url(target_date: date) -> str:
    date_stamp = target_date.strftime("%Y%m%d")
    return (
        "https://nomads.ncep.noaa.gov/pub/data/nccf/com/blend/prod/"
        f"blend.{date_stamp}/01/text/blend_nbptx.t01z"
    )


def _find_station_lines(lines: object, station_id: str) -> list[str]:
    station_prefix = f" {station_id} "
    station_lines: list[str] = []
    found_station = False

    for line in lines:
        if not isinstance(line, str):
            continue

        if line.startswith(station_prefix):
            found_station = True

        if not found_station:
            continue

        if station_lines and line.startswith(" ") and " NBM V" in line:
            break

        station_lines.append(line)

        if line.startswith(" TXNP9"):
            break

    return station_lines


def _parse_issue_time(header: str) -> datetime:
    match = re.search(
        r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{4}) UTC",
        header,
    )

    if match is None:
        raise ValueError("The NBM issue time could not be parsed.")

    value = f"{match.group(1)} {match.group(2)}"
    parsed = datetime.strptime(value, "%m/%d/%Y %H%M")
    return parsed.replace(tzinfo=timezone.utc)


def _read_row_values(row: str) -> list[int]:
    return [int(value) for value in re.findall(r"-?\d+", row)]
