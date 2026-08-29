import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass
class ForecastOutcome:
    target_date: str
    issued_at: str
    forecast_median: float
    observed_high: int | None = None


class ForecastHistory:
    """Keep real forecast/outcome pairs used for local KNYC calibration."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def record_forecast(
        self,
        target_date: date,
        issued_at: datetime,
        forecast_median: float,
    ) -> None:
        records = self._read()
        date_text = target_date.isoformat()

        if any(record.target_date == date_text for record in records):
            return

        records.append(
            ForecastOutcome(
                target_date=date_text,
                issued_at=issued_at.isoformat(),
                forecast_median=forecast_median,
            )
        )
        self._write(records)

    def record_outcome(self, target_date: date, observed_high: int) -> None:
        records = self._read()
        date_text = target_date.isoformat()
        changed = False

        for record in records:
            if record.target_date != date_text:
                continue

            if record.observed_high == observed_high:
                return

            record.observed_high = observed_high
            changed = True
            break

        if changed:
            self._write(records)

    def unresolved_dates_before(self, target_date: date) -> list[date]:
        unresolved = [
            date.fromisoformat(record.target_date)
            for record in self._read()
            if record.observed_high is None
            and date.fromisoformat(record.target_date) < target_date
        ]
        return sorted(unresolved)[-7:]

    def errors(self) -> list[float]:
        return [
            float(record.observed_high) - record.forecast_median
            for record in self._read()
            if record.observed_high is not None
        ]

    def _read(self) -> list[ForecastOutcome]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text())
        return [ForecastOutcome(**item) for item in data]

    def _write(self, records: list[ForecastOutcome]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        payload = [asdict(record) for record in records]
        temporary_path.write_text(json.dumps(payload, indent=2) + "\n")
        temporary_path.replace(self.path)
