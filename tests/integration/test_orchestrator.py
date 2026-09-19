import unittest

from services.orchestrator.input_builder import InputBuilder
from services.orchestrator.orchestrator import PredictionOrchestrator
from services.providers.gee import FeatureVector


class TestOrchestrator(unittest.TestCase):
    def test_site_feature_provenance_is_carried_to_bundle(self):
        from services.orchestrator.registry import ModelRegistry

        class FakeFeatures:
            def for_site(self, _site_id):
                return FeatureVector({
                    "sentinel2_b2": .08, "sentinel2_b3": .10, "sentinel2_b4": .13,
                    "sentinel2_b8": .25, "sentinel2_b11": .31, "sentinel2_b12": .23,
                    "ndvi": .20, "ndmi": .04, "elevation_m": 330, "slope_deg": 11,
                    "curvature": .1, "geology_class": "gondite",
                }, "GOOGLE_EARTH_ENGINE")

        orchestrator = PredictionOrchestrator(ModelRegistry(), InputBuilder(), FakeFeatures())
        request = type("Request", (), {"scenario_file": None, "prospectivity_features": None, "site_id": "MOIL-BAL-001"})()
        bundle = orchestrator.predict_all(request, request_id="req_provenance")
        self.assertEqual(bundle.feature_source, "GOOGLE_EARTH_ENGINE")
        self.assertEqual(bundle.models["prospectivity"].status, "LIVE")

    def test_all_models_are_discovered_from_registry(self):
        from services.orchestrator.registry import ModelRegistry
        registry = ModelRegistry()
        orchestrator = PredictionOrchestrator(registry, InputBuilder())
        request = type("Request", (), {"scenario_file": "scenario_02_rainfall.json", "prospectivity_features": None, "site_id": "MOIL-BAL-001"})()
        bundle = orchestrator.predict_all(request, request_id="req_test")
        self.assertEqual(bundle.request_id, "req_test")
        self.assertEqual(len(bundle.models), 7)
        self.assertEqual(bundle.models["prospectivity"].status, "UNAVAILABLE")
        self.assertEqual(bundle.models["production"].status, "LIVE")

    def test_model_failure_is_isolated(self):
        class FakeRegistry:
            def get_active_models(self):
                return {
                    "good": {"version": "v001", "status": "LIVE", "type": "ML", "source": "fixture", "predict_module": "models.prospectivity.v001.predict", "input_mode": "feature_vector"},
                    "bad": {"version": "v001", "status": "LIVE", "type": "ML", "source": "fixture", "predict_module": "models.prospectivity.v001.predict", "input_mode": "feature_vector"},
                }

            def get_model(self, model_id):
                return self.get_active_models().get(model_id)

            def import_predict(self, model_id, entry):
                if model_id == "bad":
                    def fail(_payload):
                        raise RuntimeError("forced test failure")
                    return fail
                from schemas.contracts import ModelResult
                def good(_payload):
                    return ModelResult(model_id="good", model_version="v001", status="LIVE", data_source="fixture", prediction=0.5)
                return good

        class FakeBuilder(InputBuilder):
            def build_model_input(self, meta, *, scenario_filename, features, site_id):
                return {
                    "sentinel2_b2": 0.08, "sentinel2_b3": 0.10, "sentinel2_b4": 0.13,
                    "sentinel2_b8": 0.25, "sentinel2_b11": 0.31, "sentinel2_b12": 0.23,
                    "ndvi": 0.20, "ndmi": 0.04, "elevation_m": 330, "slope_deg": 11,
                    "curvature": 0.1, "geology_class": "gondite",
                }

        orchestrator = PredictionOrchestrator(FakeRegistry(), FakeBuilder())
        request = type("Request", (), {"scenario_file": "scenario_01_normal.json", "prospectivity_features": {}, "site_id": None})()
        bundle = orchestrator.predict_all(request, request_id="req_failure")
        self.assertEqual(bundle.models["good"].status, "LIVE")
        self.assertEqual(bundle.models["bad"].status, "UNAVAILABLE")
        self.assertIn("forced test failure", bundle.models["bad"].reason)
