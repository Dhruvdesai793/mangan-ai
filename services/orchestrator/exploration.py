"""Repository-local prospectivity map loading with process-level caching.

The demonstration map is generated offline by scripts/generate_prospectivity_map_cache.py
from the same frozen model/data pair. The API loads that cache instead of performing
2,000 expensive single-row inference calls during every application start.
"""
from __future__ import annotations

import json
import pathlib
import threading
import time
from typing import Any

from services.orchestrator.registry import ModelRegistry


class ExplorationMapService:
    CACHE_FILENAME = "prospectivity_map_demo_v001.json"

    def __init__(
        self,
        registry: ModelRegistry,
        repo_root: pathlib.Path | None = None,
        cache_seconds: int = 300,
    ) -> None:
        self.registry = registry
        self.repo_root = repo_root or pathlib.Path(__file__).resolve().parents[2]
        self.cache_path = self.repo_root / "services" / "orchestrator" / "cache" / self.CACHE_FILENAME
        self.cache_seconds = max(0, cache_seconds)
        self._cache: tuple[float, list[dict[str, Any]]] | None = None
        self._lock = threading.Lock()

    def get_points(self, limit: int = 2000, min_score: float | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 2000))
        base = self._get_cached_points()
        if min_score is not None:
            base = [point for point in base if point["prospectivity"] >= min_score]
        return base[:limit]

    def metadata(self) -> dict[str, Any]:
        meta = self.registry.get_model("prospectivity") or {}
        return {
            "data_source": "PUBLIC_DATA_SYNTHETIC_FALLBACK",
            "model_version": meta.get("version", "unknown"),
        }

    def _get_cached_points(self) -> list[dict[str, Any]]:
        now = time.monotonic()
        if self._cache and (self.cache_seconds == 0 or now - self._cache[0] < self.cache_seconds):
            return list(self._cache[1])

        with self._lock:
            now = time.monotonic()
            if self._cache and (self.cache_seconds == 0 or now - self._cache[0] < self.cache_seconds):
                return list(self._cache[1])
            points = self._load_cache()
            self._cache = (time.monotonic(), points)
            return list(points)

    def _load_cache(self) -> list[dict[str, Any]]:
        if not self.cache_path.is_file():
            raise FileNotFoundError(
                f"prospectivity map cache not found: {self.cache_path}. "
                "Run scripts/generate_prospectivity_map_cache.py first."
            )
        with self.cache_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        expected_version = (self.registry.get_model("prospectivity") or {}).get("version")
        if payload.get("model_version") != expected_version:
            raise ValueError(
                f"map cache model version {payload.get('model_version')!r} does not match "
                f"registry version {expected_version!r}"
            )
        points = payload.get("points")
        if not isinstance(points, list) or not points:
            raise ValueError("prospectivity map cache contains no points")
        return points
