import unittest

from services.decision_engine.engine import DecisionEngine
from models._demo_common import load_active_scenario
from models.production.demo_v001.predict import predict as production_predict
from models.equipment.demo_v001.predict import predict as equipment_predict
from models.weather.demo_v001.predict import predict as weather_predict
from models.recovery.demo_v001.predict import predict as recovery_predict
from models.blast.demo_v001.predict import predict as blast_predict
from models.grade.demo_v001.predict import predict as grade_predict
from schemas.contracts import ModelResult


class TestDecisionPipeline(unittest.TestCase):
    def _models(self, scenario):
        inp = {"scenario_file": scenario}
        return {
            "production": production_predict(inp),
            "equipment": equipment_predict(inp),
            "weather": weather_predict(inp),
            "recovery": recovery_predict(inp),
            "blast": blast_predict(inp),
            "grade": grade_predict(inp),
        }

    def test_rainfall_scenario_produces_expected_drivers(self):
        result = DecisionEngine().evaluate(self._models("scenario_02_rainfall.json"))
        self.assertEqual(result["risk_level"], "HIGH")
        self.assertIn("production_shortfall", result["primary_drivers"])
        self.assertIn("equipment_availability", result["primary_drivers"])
        self.assertIn("weather", result["primary_drivers"])
        self.assertTrue(all(action["requires_human_approval"] for action in result["recommended_actions"]))

    def test_unavailable_model_becomes_limitation(self):
        models = self._models("scenario_01_normal.json")
        models["weather"] = ModelResult(
            model_id="weather", model_version="demo_v001", status="UNAVAILABLE",
            data_source="SYNTHETIC_SCENARIO", reason="forced unavailable",
        )
        result = DecisionEngine().evaluate(models)
        self.assertTrue(any("weather" in item for item in result["limitations"]))


if __name__ == "__main__":
    unittest.main()
