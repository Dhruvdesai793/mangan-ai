"""Registry-driven, fault-isolated specialist-model orchestration."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Mapping

from schemas.contracts import ModelResult
from services.orchestrator.contracts import PredictionBundle, validate_model_result
from services.orchestrator.input_builder import InputBuilder
from services.orchestrator.registry import ModelRegistry
from services.providers.features import SiteFeatureService

class PredictionOrchestrator:
    def __init__(self, registry: ModelRegistry, input_builder: InputBuilder, feature_service: SiteFeatureService | None = None) -> None:
        self.registry = registry
        self.input_builder = input_builder
        self.feature_service = feature_service

    def predict_all(self, request: Any, *, request_id: str | None = None) -> PredictionBundle:
        request_id = request_id or f"req_{uuid.uuid4().hex[:12]}"
        scenario_file = self.input_builder.resolve_scenario_filename(getattr(request, "scenario_file", None))
        scenario = self.input_builder.load_scenario(scenario_file)
        feature_model = getattr(request, "prospectivity_features", None)
        features = feature_model.supplied() if feature_model is not None and hasattr(feature_model, "supplied") else feature_model
        site_id = getattr(request, "site_id", None)

        feature_limitation = None
        feature_source = "CALLER_SUPPLIED_FEATURES" if features else None
        if not features and site_id and self.feature_service:
            try:
                feature_vector = self.feature_service.for_site(site_id)
                features = feature_vector.features
                feature_limitation = feature_vector.limitation
                feature_source = feature_vector.data_source
            except Exception as exc:
                feature_limitation = f"Automated geospatial feature extraction failed: {type(exc).__name__}: {exc}"

        models: dict[str, ModelResult] = {}
        limitations: list[str] = []
        if feature_limitation:
            limitations.append(feature_limitation)
        for model_id, meta in self.registry.get_active_models().items():
            models[model_id] = self.predict_one(
                model_id, meta=meta, scenario_file=scenario_file, scenario=scenario, features=features, site_id=site_id
            )
            result = models[model_id]
            if result.status == "UNAVAILABLE" and result.reason:
                limitations.append(f"{model_id}: {result.reason}")

        if any(result.status == "DEMO" for result in models.values()):
            limitations.append("Operational demonstration modules use synthetic scenario data.")
        if not site_id:
            limitations.append("site_id was not supplied; site-reference models may be unavailable.")
        if not features and models.get("prospectivity") and models["prospectivity"].status == "UNAVAILABLE":
            limitations.append("Prospectivity was not evaluated because no feature vector was supplied.")

        return PredictionBundle(
            request_id=request_id,
            scenario_id=str(scenario["scenario_id"]),
            models=models,
            limitations=list(dict.fromkeys(limitations)),
            feature_source=feature_source,
        )

    def predict_one(self, model_id: str, *, meta: Mapping[str, Any] | None = None, scenario_file: str, scenario: Mapping[str, Any], features: Mapping[str, Any] | None, site_id: str | None) -> ModelResult:
        meta = meta or self.registry.get_model(model_id)
        if meta is None:
            return self._unavailable(model_id, "model is not present in the trusted registry")
        if meta["status"] == "UNAVAILABLE":
            return self._unavailable(model_id, "model is marked UNAVAILABLE in the registry", version=meta["version"], data_source=meta.get("source") or "REGISTRY")
        try:
            model_input = self.input_builder.build_model_input(meta, scenario_filename=scenario_file, features=features, site_id=site_id)
            if model_input is None:
                mode = meta.get("input_mode")
                missing = "prospectivity feature vector" if mode == "feature_vector" else "site_id" if mode == "site_reference" else "model input"
                return self._unavailable(model_id, f"required {missing} was not supplied", version=meta["version"], data_source=meta.get("source") or "BACKEND_INPUT_BUILDER")
            predict = self.registry.import_predict(model_id, dict(meta))
            result = predict(model_input)
            return validate_model_result(result, model_id, meta["version"])
        except Exception as exc:
            return self._unavailable(model_id, f"model execution failed: {type(exc).__name__}: {exc}", version=meta["version"], data_source=meta.get("source") or "BACKEND_ORCHESTRATOR")

    @staticmethod
    def _unavailable(model_id: str, reason: str, *, version: str = "unknown", data_source: str = "BACKEND_ORCHESTRATOR") -> ModelResult:
        return ModelResult(model_id=model_id, model_version=version, status="UNAVAILABLE", data_source=data_source, prediction=None, uncertainty=None, reason=reason, prediction_timestamp=datetime.now(timezone.utc).isoformat())
