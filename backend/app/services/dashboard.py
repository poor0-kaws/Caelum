from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.clients.http import JsonHttpClient
from app.clients.kalshi import KalshiClient
from app.clients.nbm import NbmClient, NbmTemperatureGuidance
from app.clients.nws import NwsClient
from app.config import Settings
from app.models import DashboardData
from app.services.history import ForecastHistory
from app.services.probability import choose_probability_model
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
        self.history = ForecastHistory(settings.history_path)
        self.guidance_cache: dict[date, NbmTemperatureGuidance] = {}

    def build(self) -> DashboardData:
        timezone = ZoneInfo("America/New_York")
        target_date = datetime.now(timezone).date()
        nws = NwsClient(self.settings, self.http)
        weather = nws.get_weather()
        markets = KalshiClient(self.settings, self.http).get_open_markets()
        guidance = self._get_guidance(target_date)

        self.history.record_forecast(
            target_date=target_date,
            issued_at=guidance.issued_at,
            forecast_median=guidance.percentiles[50],
        )
        self._resolve_past_outcomes(nws, target_date)

        probability_model, model_summary = choose_probability_model(
            guidance=guidance,
            historical_errors=self.history.errors(),
            observed_high=weather.observed_high,
            minimum_calibration_days=self.settings.minimum_calibration_days,
        )
        scored_markets, recommendation = score_markets(
            markets,
            probability_model,
            weather.projected_high,
        )

        return DashboardData(
            source="live",
            generated_at=datetime.now().astimezone(),
            notice=EDUCATIONAL_NOTICE,
            weather=weather,
            model=model_summary,
            recommendation=recommendation,
            markets=scored_markets,
        )

    def _resolve_past_outcomes(
        self,
        nws: NwsClient,
        target_date: date,
    ) -> None:
        for unresolved_date in self.history.unresolved_dates_before(target_date):
            try:
                observed_high = nws.get_observed_high(unresolved_date)
            except Exception:
                continue

            if observed_high is None:
                continue

            self.history.record_outcome(unresolved_date, observed_high)

    def _get_guidance(self, target_date: date) -> NbmTemperatureGuidance:
        cached_guidance = self.guidance_cache.get(target_date)
        if cached_guidance is not None:
            return cached_guidance

        guidance = NbmClient(
            self.http,
            self.settings.station_id,
        ).get_daily_maximum_guidance(target_date)
        self.guidance_cache[target_date] = guidance
        return guidance
