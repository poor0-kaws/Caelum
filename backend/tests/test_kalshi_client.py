import unittest

from app.clients.kalshi import parse_market


class KalshiParserTests(unittest.TestCase):
    def test_parses_bounded_range_from_yes_subtitle(self) -> None:
        market = parse_market(
            _market_data(
                ticker="KXHIGHNY-26AUG29-B85.5",
                title="Will the maximum temperature be 85-86° on Aug 29, 2026?",
                yes_sub_title="85° to 86°",
                floor_strike=85,
                cap_strike=86,
            )
        )

        self.assertIsNotNone(market)
        assert market is not None
        self.assertEqual(market.minimum_temperature, 85)
        self.assertEqual(market.maximum_temperature, 86)
        self.assertEqual(market.range_label, "85-86°F")

    def test_uses_displayed_value_for_or_above_market(self) -> None:
        market = parse_market(
            _market_data(
                ticker="KXHIGHNY-26AUG29-T86",
                title="Will the maximum temperature be >86° on Aug 29, 2026?",
                yes_sub_title="87° or above",
                floor_strike=86,
            )
        )

        self.assertIsNotNone(market)
        assert market is not None
        self.assertEqual(market.minimum_temperature, 87)
        self.assertIsNone(market.maximum_temperature)
        self.assertEqual(market.range_label, "87°F or above")

    def test_uses_displayed_value_for_or_below_market(self) -> None:
        market = parse_market(
            _market_data(
                ticker="KXHIGHNY-26AUG29-T79",
                title="Will the maximum temperature be <79° on Aug 29, 2026?",
                yes_sub_title="78° or below",
                cap_strike=79,
            )
        )

        self.assertIsNotNone(market)
        assert market is not None
        self.assertIsNone(market.minimum_temperature)
        self.assertEqual(market.maximum_temperature, 78)
        self.assertEqual(market.range_label, "78°F or below")


def _market_data(
    *,
    ticker: str,
    title: str,
    yes_sub_title: str,
    floor_strike: int | None = None,
    cap_strike: int | None = None,
) -> dict:
    return {
        "ticker": ticker,
        "title": title,
        "yes_sub_title": yes_sub_title,
        "floor_strike": floor_strike,
        "cap_strike": cap_strike,
        "yes_bid_dollars": "0.4300",
        "yes_ask_dollars": "0.4500",
        "no_ask_dollars": "0.5700",
        "volume_fp": "123.00",
        "status": "open",
    }


if __name__ == "__main__":
    unittest.main()
