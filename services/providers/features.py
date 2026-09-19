"""Cached site-to-feature service that keeps provider and model concerns separate."""
from __future__ import annotations

from config import Settings, get_settings
from services.persistence.repositories import SatelliteFeatureRepository
from services.providers.gee import FeatureVector, GeeProvider, PIPELINE_VERSION


class SiteFeatureService:
    def __init__(self, provider: GeeProvider, repository: SatelliteFeatureRepository | None = None, settings: Settings | None = None) -> None:
        self.provider = provider
        self.repository = repository
        self.settings = settings or get_settings()

    def for_site(self, site_id: str) -> FeatureVector:
        key = f"{site_id}:{self.settings.gee_start_date}:{self.settings.gee_end_date}:{PIPELINE_VERSION}"
        if self.repository:
            try:
                cached = self.repository.get(key)
                if cached:
                    return FeatureVector(cached, "POSTGRES_GEE_FEATURE_CACHE")
            except Exception:
                pass
        result = self.provider.extract(site_id)
        if self.repository and result.data_source == "GOOGLE_EARTH_ENGINE":
            try:
                self.repository.put(
                    cache_key=key, site_id=site_id, date_start=self.settings.gee_start_date,
                    date_end=self.settings.gee_end_date, pipeline_version=PIPELINE_VERSION,
                    data_source=result.data_source, features=result.features,
                )
            except Exception:
                pass
        return result
