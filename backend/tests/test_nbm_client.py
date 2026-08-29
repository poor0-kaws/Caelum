import unittest
from datetime import date, timezone

from app.clients.nbm import parse_station_guidance


class NbmParserTests(unittest.TestCase):
    def test_reads_first_daily_maximum_from_each_percentile_row(self) -> None:
        lines = [
            " KNYC    NBM V5.0 NBP GUIDANCE    8/29/2026  0100 UTC",
            "        SUN 30| MON 31| TUE 01",
            " TXNP1  77  60| 81  67| 78  66",
            " TXNP2  78  61| 82  68| 80  67",
            " TXNP5  79  64| 83  70| 81  69",
            " TXNP7  80  65| 84  71| 82  70",
            " TXNP9  81  66| 86  72| 84  71",
        ]

        guidance = parse_station_guidance(lines, date(2026, 8, 29))

        self.assertEqual(
            guidance.percentiles,
            {10: 77.0, 25: 78.0, 50: 79.0, 75: 80.0, 90: 81.0},
        )
        self.assertEqual(guidance.issued_at.tzinfo, timezone.utc)
        self.assertEqual(guidance.issued_at.hour, 1)

    def test_rejects_an_incomplete_percentile_block(self) -> None:
        lines = [
            " KNYC    NBM V5.0 NBP GUIDANCE    8/29/2026  0100 UTC",
            " TXNP5  79  64| 83  70",
        ]

        with self.assertRaises(ValueError):
            parse_station_guidance(lines, date(2026, 8, 29))


if __name__ == "__main__":
    unittest.main()
