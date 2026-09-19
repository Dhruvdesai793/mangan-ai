"""Shared FastAPI dependencies and service construction."""
from __future__ import annotations

from functools import lru_cache

from services.decision_engine.engine import DecisionEngine
from services.orchestrator.exploration import ExplorationMapService
from services.orchestrator.input_builder import InputBuilder
from services.orchestrator.orchestrator import PredictionOrchestrator
from services.orchestrator.registry import ModelRegistry
from services.providers.moil_reference import MoilReferenceProvider
from config import get_settings
from services.persistence.repositories import MineRepository, PredictionRepository, SatelliteFeatureRepository
from services.persistence.session import Database
from services.providers.features import SiteFeatureService
from services.providers.gee import GeeProvider
from services.jobs.job_store import JobStore
from services.persistence.repositories import DatabaseJobRepository


@lru_cache(maxsize=1)
def get_registry() -> ModelRegistry:
    return ModelRegistry()


@lru_cache(maxsize=1)
def get_input_builder() -> InputBuilder:
    return InputBuilder()


@lru_cache(maxsize=1)
def get_database() -> Database:
    return Database()


def database_available() -> bool:
    return get_database().ping()


@lru_cache(maxsize=1)
def get_mine_repository() -> MineRepository | None:
    return MineRepository(get_database()) if database_available() else None


@lru_cache(maxsize=1)
def get_prediction_repository() -> PredictionRepository | None:
    return PredictionRepository(get_database()) if database_available() else None


@lru_cache(maxsize=1)
def get_job_store() -> JobStore:
    repository = DatabaseJobRepository(get_database()) if database_available() else None
    return JobStore(repository)


@lru_cache(maxsize=1)
def get_site_feature_service() -> SiteFeatureService | None:
    settings = get_settings()
    if settings.mangan_env == "test":
        return None
    cache = SatelliteFeatureRepository(get_database()) if database_available() else None
    return SiteFeatureService(GeeProvider(settings=settings, reference=get_moil_provider()), cache, settings)


@lru_cache(maxsize=1)
def get_orchestrator() -> PredictionOrchestrator:
    return PredictionOrchestrator(get_registry(), get_input_builder(), get_site_feature_service())


@lru_cache(maxsize=1)
def get_decision_engine() -> DecisionEngine:
    return DecisionEngine()


@lru_cache(maxsize=1)
def get_exploration_map_service() -> ExplorationMapService:
    return ExplorationMapService(get_registry())


@lru_cache(maxsize=1)
def get_moil_provider() -> MoilReferenceProvider:
    return MoilReferenceProvider(repository=get_mine_repository())
