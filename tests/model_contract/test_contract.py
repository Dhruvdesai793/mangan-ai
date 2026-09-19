import sys, json, pathlib, importlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from schemas.contracts import VALID_STATUSES

ROOT = pathlib.Path(__file__).resolve().parents[2]
with open(ROOT / "schemas" / "model_registry.json") as f:
    REGISTRY = json.load(f)

SAMPLE_INPUT = {
    "sentinel2_b2": 0.08, "sentinel2_b3": 0.10, "sentinel2_b4": 0.13,
    "sentinel2_b8": 0.25, "sentinel2_b11": 0.31, "sentinel2_b12": 0.23,
    "ndvi": 0.20, "ndmi": 0.04, "elevation_m": 330, "slope_deg": 11,
    "curvature": 0.1, "geology_class": "gondite",
}

class TestModelContract(unittest.TestCase):
    def test_registry_not_empty(self):
        self.assertEqual(len(REGISTRY), 7)
        self.assertEqual(sum(m["status"] == "LIVE" for m in REGISTRY.values()), 3)
        self.assertEqual(sum(m["status"] == "DEMO" for m in REGISTRY.values()), 4)

    def test_every_registered_model_returns_valid_contract(self):
        for model_id, meta in REGISTRY.items():
            with self.subTest(model=model_id):
                module = importlib.import_module(meta["predict_module"])
                if meta["input_mode"] == "feature_vector":
                    payload = SAMPLE_INPUT
                elif meta["input_mode"] == "site_reference":
                    payload = {"site_id": "MOIL-BAL-001"}
                else:
                    payload = {"scenario_file": "scenario_01_normal.json"}
                result = module.predict(payload).to_dict()
                self.assertEqual(result["model_id"], model_id)
                self.assertIn(result["status"], VALID_STATUSES)
                self.assertTrue(result["data_source"])
                self.assertTrue(result["prediction_timestamp"])
                self.assertNotEqual(result["status"], "UNAVAILABLE", result.get("reason"))

    def test_prospectivity_missing_fields_returns_unavailable_not_crash(self):
        module = importlib.import_module(REGISTRY["prospectivity"]["predict_module"])
        result = module.predict({}).to_dict()
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertTrue(result["reason"])

    def test_grade_reference_scope(self):
        module = importlib.import_module(REGISTRY["grade"]["predict_module"])
        result = module.predict({"site_id": "MOIL-BAL-001"}).to_dict()
        self.assertEqual(result["status"], "LIVE")
        self.assertEqual(result["prediction"]["scope"], "VERIFIED_PRODUCT_GRADE_REFERENCE_NOT_IN_SITU_SPATIAL_PREDICTION")

    def test_production_reference_scope(self):
        module = importlib.import_module(REGISTRY["production"]["predict_module"])
        result = module.predict({"site_id": "MOIL-BAL-001"}).to_dict()
        self.assertEqual(result["status"], "LIVE")
        self.assertEqual(result["prediction"]["scope"], "OFFICIAL_HISTORICAL_REFERENCE_NOT_FUTURE_FORECAST")

if __name__ == "__main__":
    unittest.main()
