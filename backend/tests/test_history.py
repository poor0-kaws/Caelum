import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from app.services.history import ForecastHistory


class ForecastHistoryTests(unittest.TestCase):
    def test_records_one_forecast_and_its_later_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            history = ForecastHistory(Path(directory) / "history.json")
            target_date = date(2026, 8, 29)

            history.record_forecast(
                target_date=target_date,
                issued_at=datetime(2026, 8, 29, 1, tzinfo=timezone.utc),
                forecast_median=79,
            )
            history.record_forecast(
                target_date=target_date,
                issued_at=datetime(2026, 8, 29, 1, tzinfo=timezone.utc),
                forecast_median=99,
            )
            history.record_outcome(target_date, observed_high=81)

            self.assertEqual(history.errors(), [2.0])

    def test_only_returns_unresolved_past_dates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            history = ForecastHistory(Path(directory) / "history.json")
            yesterday = date(2026, 8, 28)
            today = date(2026, 8, 29)

            history.record_forecast(
                yesterday,
                datetime(2026, 8, 28, 1, tzinfo=timezone.utc),
                80,
            )
            history.record_forecast(
                today,
                datetime(2026, 8, 29, 1, tzinfo=timezone.utc),
                79,
            )

            self.assertEqual(history.unresolved_dates_before(today), [yesterday])


if __name__ == "__main__":
    unittest.main()
