"""Translate API requests into model-specific inputs without hardcoding model lists."""
from __future__ import annotations

import json
import pathlib
from typing import Any, Mapping

class InputBuilder:
    def __init__(self, repo_root: pathlib.Path | None = None) -> None:
        self.repo_root = repo_root or pathlib.Path(__file__).resolve().parents[2]
        self.scenarios_dir = (self.repo_root / "scenarios").resolve()

    def resolve_scenario_filename(self, scenario_file: str | None) -> str:
        filename = scenario_file or self._default_scenario()
        path = self._safe_scenario_path(filename)
        return path.name

    def load_scenario(self, scenario_file: str | None) -> dict[str, Any]:
        filename = self.resolve_scenario_filename(scenario_file)
        path = self._safe_scenario_path(filename)
        with path.open("r", encoding="utf-8") as handle:
            scenario = json.load(handle)
        self._validate_scenario(scenario, filename)
        return scenario

    def build_model_input(self, meta: Mapping[str, Any], *, scenario_filename: str, features: Mapping[str, Any] | None, site_id: str | None) -> dict[str, Any] | None:
        mode = meta.get("input_mode")
        if mode == "feature_vector":
            return dict(features) if features else None
        if mode == "site_reference":
            return {"site_id": site_id} if site_id else None
        if mode == "scenario":
            return {"scenario_file": scenario_filename}
        raise ValueError(f"unsupported model input_mode: {mode!r}")

    def _default_scenario(self) -> str:
        config_path = self.repo_root / "configs" / "models.yaml"
        if config_path.exists():
            try:
                import yaml
                with config_path.open("r", encoding="utf-8") as handle:
                    config = yaml.safe_load(handle) or {}
                candidate = config.get("active_scenario_default")
                if candidate:
                    return str(candidate)
            except Exception:
                pass
        active_file = self.scenarios_dir / "_active_scenario.txt"
        if active_file.exists():
            candidate = active_file.read_text(encoding="utf-8").strip()
            if candidate:
                return candidate
        return "scenario_01_normal.json"

    def _safe_scenario_path(self, filename: str) -> pathlib.Path:
        if not isinstance(filename, str) or not filename:
            raise ValueError("scenario_file must be a non-empty filename")
        candidate = pathlib.Path(filename)
        if candidate.name != filename or candidate.suffix.lower() != ".json":
            raise ValueError("scenario_file must be a scenario JSON filename")
        if not filename.startswith("scenario_"):
            raise ValueError("scenario_file must start with 'scenario_'")
        path = (self.scenarios_dir / filename).resolve()
        try:
            path.relative_to(self.scenarios_dir)
        except ValueError as exc:
            raise ValueError("scenario_file resolves outside the scenarios directory") from exc
        if not path.is_file():
            raise FileNotFoundError(f"scenario file not found: {filename}")
        return path

    @staticmethod
    def _validate_scenario(scenario: Mapping[str, Any], filename: str) -> None:
        if not isinstance(scenario, Mapping):
            raise ValueError(f"scenario {filename!r} must contain a JSON object")
        required = {"scenario_id", "mine", "zone", "weather", "equipment", "production", "recovery", "blast", "grade"}
        missing = required - set(scenario)
        if missing:
            raise ValueError(f"scenario {filename!r} missing required sections: {sorted(missing)}")
