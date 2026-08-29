from datetime import datetime

from app.clients.http import JsonHttpClient
from app.clients.kalshi import KalshiClient
from app.clients.nws import NwsClient
from app.config import Settings
from app.models import DashboardData
from app.sample_data import sample_markets, sample_weather
from app.services.recommendation import score_markets


EDUCATIONAL_NOTICE = (
    "Educational dashboard only. It reads public data, does not place trades, "
    "and does not provide financial advice."
)


class DashboardService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.http = JsonHttpClient(
            timeout_seconds=settings.request_timeout_seconds,
            user_agent=settings.user_agent,
        )

    def build(self, mode: str) -> DashboardData:
        if mode == "sample":
            return self._build_sample()

        weather = NwsClient(self.settings, self.http).get_weather()
        markets = KalshiClient(self.settings, self.http).get_open_markets()
        scored_markets, recommendation = score_markets(markets, weather.projected_high)

        return DashboardData(
            source="live",
            generated_at=datetime.now().astimezone(),
            notice=EDUCATIONAL_NOTICE,
            weather=weather,
            recommendation=recommendation,
            markets=scored_markets,
        )

    def _build_sample(self) -> DashboardData:
        weather = sample_weather()
        markets, recommendation = score_markets(
            sample_markets(),
            weather.projected_high,
        )

        return DashboardData(
            source="sample",
            generated_at=datetime.now().astimezone(),
            notice=EDUCATIONAL_NOTICE,
            weather=weather,
            recommendation=recommendation,
            markets=markets,
        )
