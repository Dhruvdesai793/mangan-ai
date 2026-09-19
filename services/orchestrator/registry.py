"""Trusted, registry-driven model discovery and loading."""
from __future__ import annotations

import copy
import importlib
import importlib.util
import json
import pathlib
import sys
from typing import Any, Callable

from schemas.contracts import ModelResult


class ModelRegistry:
    """Loads and validates the repository-owned model registry."""

    VALID_STATUSES = {"LIVE", "DEMO", "UNAVAILABLE"}
    REQUIRED_KEYS = {"version", "status", "type", "source", "predict_module", "input_mode"}

    def __init__(self, registry_path: pathlib.Path | None = None) -> None:
        self.repo_root = pathlib.Path(__file__).resolve().parents[2]
        self.registry_path = registry_path or self.repo_root / "schemas" / "model_registry.json"
        self._models: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        with self.registry_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        self._models = self._validate(raw)

        root = str(self.repo_root)
        if root not in sys.path:
            sys.path.insert(0, root)

    def refresh(self) -> None:
        self.load()

    def get_active_models(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(self._models)

    def get_model(self, model_id: str) -> dict[str, Any] | None:
        entry = self._models.get(model_id)
        return copy.deepcopy(entry) if entry else None

    def summary(self) -> dict[str, int]:
        counts = {"total_models": len(self._models), "live": 0, "demo": 0, "unavailable": 0}
        for entry in self._models.values():
            status = entry["status"].lower()
            counts[status] = counts.get(status, 0) + 1
        return counts

    def import_predict(self, model_id: str, entry: dict[str, Any]) -> Callable[[dict], ModelResult]:
        """Import only the predict module explicitly approved by the trusted registry."""
        if model_id not in self._models:
            raise KeyError(f"unknown model id: {model_id}")
        trusted = self._models[model_id]
        if trusted != entry:
            raise ValueError(f"registry entry for {model_id!r} does not match the loaded registry")

        if trusted["status"] == "UNAVAILABLE":
            raise RuntimeError(f"model {model_id!r} is marked UNAVAILABLE in the registry")

        module_name = trusted["predict_module"]
        if not module_name.startswith("models."):
            raise ValueError("registry predict_module must be rooted under models")
        if ".." in module_name or "/" in module_name or "\\" in module_name:
            raise ValueError("invalid registry predict_module")

        module = importlib.import_module(module_name)
        spec = importlib.util.find_spec(module_name)
        if spec is None or not spec.origin or spec.origin in {"built-in", "frozen"}:
            raise ImportError(f"cannot resolve trusted model module: {module_name}")

        origin = pathlib.Path(spec.origin).resolve()
        models_root = (self.repo_root / "models").resolve()
        try:
            origin.relative_to(models_root)
        except ValueError as exc:
            raise ImportError("resolved model module is outside the trusted models directory") from exc

        predict = getattr(module, "predict", None)
        if not callable(predict):
            raise AttributeError(f"trusted module {module_name} does not expose callable predict")
        return predict

    @classmethod
    def _validate(cls, raw: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(raw, dict) or not raw:
            raise ValueError("model registry must be a non-empty JSON object")

        validated: dict[str, dict[str, Any]] = {}
        for model_id, entry in raw.items():
            if not isinstance(model_id, str) or not model_id.strip():
                raise ValueError("registry model ids must be non-empty strings")
            if not isinstance(entry, dict):
                raise ValueError(f"registry entry for {model_id!r} must be an object")
            missing = cls.REQUIRED_KEYS - set(entry)
            if missing:
                raise ValueError(f"registry entry {model_id!r} missing keys: {sorted(missing)}")
            if entry["status"] not in cls.VALID_STATUSES:
                raise ValueError(f"registry entry {model_id!r} has invalid status {entry['status']!r}")
            if not isinstance(entry["version"], str) or not entry["version"]:
                raise ValueError(f"registry entry {model_id!r} has invalid version")
            if not isinstance(entry["predict_module"], str) or not entry["predict_module"]:
                raise ValueError(f"registry entry {model_id!r} has invalid predict_module")
            if entry["input_mode"] not in {"feature_vector", "site_reference", "scenario"}:
                raise ValueError(f"registry entry {model_id!r} has invalid input_mode {entry['input_mode']!r}")
            validated[model_id] = copy.deepcopy(entry)
        return validated
