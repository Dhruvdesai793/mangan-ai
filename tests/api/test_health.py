import os
import unittest

from fastapi.testclient import TestClient

os.environ["MANGAN_ENV"] = "test"

from services.api.main import app


class TestHealthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["service"], "mangan-ai-api")
        self.assertEqual(body["registry"]["total_models"], 7)
        self.assertEqual(body["registry"]["live"], 3)
        self.assertEqual(body["registry"]["demo"], 4)
        self.assertEqual(body["registry"]["unavailable"], 0)
        self.assertTrue(response.headers.get("X-Request-ID"))
