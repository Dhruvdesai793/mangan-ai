import os
import unittest

from fastapi.testclient import TestClient

os.environ["MANGAN_ENV"] = "test"
from services.api.main import app


class TestExplorationAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_map_returns_map_ready_json(self):
        response = self.client.post("/exploration/map", json={"limit": 5})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["model_version"], "v001")
        self.assertEqual(body["point_count"], 5)
        self.assertEqual(body["data_source"], "PUBLIC_DATA_SYNTHETIC_FALLBACK")
        self.assertEqual(len(body["points"]), 5)
        for point in body["points"]:
            self.assertIn("latitude", point)
            self.assertIn("longitude", point)
            self.assertIn("prospectivity", point)
            self.assertIn(point["status"], {"LIVE", "DEMO", "UNAVAILABLE"})
