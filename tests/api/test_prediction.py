import os
import unittest

from fastapi.testclient import TestClient

os.environ["MANGAN_ENV"] = "test"
from services.api.main import app


FEATURES = {
    "sentinel2_b2": 0.08, "sentinel2_b3": 0.10, "sentinel2_b4": 0.13,
    "sentinel2_b8": 0.25, "sentinel2_b11": 0.31, "sentinel2_b12": 0.23,
    "ndvi": 0.20, "ndmi": 0.04, "elevation_m": 330, "slope_deg": 11,
    "curvature": 0.1, "geology_class": "gondite",
}


class TestPredictionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_valid_prospectivity_is_live(self):
        response = self.client.post("/predict/prospectivity", json={"features": FEATURES})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["model_id"], "prospectivity")
        self.assertEqual(body["model_version"], "v001")
        self.assertEqual(body["status"], "LIVE")
        self.assertIsNotNone(body["prediction"])

    def test_incomplete_prospectivity_is_unavailable(self):
        response = self.client.post("/predict/prospectivity", json={"features": {"ndvi": 0.1}})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "UNAVAILABLE")
        self.assertTrue(body["reason"])

    def test_predict_all_contains_every_registered_model(self):
        response = self.client.post(
            "/predict/all",
            json={"scenario_file": "scenario_02_rainfall.json", "site_id": "MOIL-BAL-001", "prospectivity_features": FEATURES},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["feature_source"], "CALLER_SUPPLIED_FEATURES")
        self.assertEqual(set(body["models"]), {
            "blast", "equipment", "grade", "production", "prospectivity", "recovery", "weather"
        })
        self.assertEqual(body["models"]["prospectivity"]["status"], "LIVE")
        self.assertIn("prospectivity", body["decision"]["context"])
        self.assertFalse(any(item.startswith("prospectivity:") for item in body["limitations"]))
        self.assertEqual(body["models"]["grade"]["status"], "LIVE")
        self.assertEqual(body["models"]["production"]["status"], "LIVE")
        for model_id in body["models"]:
            if model_id not in {"prospectivity", "grade", "production"}:
                self.assertEqual(body["models"][model_id]["status"], "DEMO")

    def test_predict_all_without_prospectivity_features_is_honest(self):
        response = self.client.post("/predict/all", json={"scenario_file": "scenario_02_rainfall.json"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["models"]["prospectivity"]["status"], "UNAVAILABLE")
        self.assertEqual(body["models"]["grade"]["status"], "UNAVAILABLE")
        self.assertEqual(body["models"]["production"]["status"], "UNAVAILABLE")
        self.assertTrue(any("Prospectivity" in item for item in body["limitations"]))

    def test_bad_scenario_is_rejected(self):
        response = self.client.post("/predict/all", json={"scenario_file": "../secrets.json"})
        self.assertIn(response.status_code, {400, 422})
        self.assertTrue(response.json().get("detail"))

    def test_reference_models_are_live_with_site_id(self):
        response = self.client.post("/predict/all", json={"site_id": "MOIL-BAL-001", "scenario_file": "scenario_02_rainfall.json"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["models"]["grade"]["status"], "LIVE")
        self.assertEqual(body["models"]["production"]["status"], "LIVE")
        self.assertEqual(body["models"]["grade"]["prediction"]["mn_grade_percent"], 47.0)
        self.assertEqual(body["models"]["production"]["prediction"]["historical_production_tonnes"], 277329.0)

    def test_mines_and_lease_routes(self):
        response = self.client.get("/mines")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 10)
        response = self.client.get("/mines/MOIL-BAL-001/leases")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["type"], "FeatureCollection")
        self.assertGreaterEqual(len(response.json()["features"]), 1)
