import os
import unittest

from fastapi.testclient import TestClient

os.environ["MANGAN_ENV"] = "test"
from services.api.main import app


class TestJobsAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_predict_all_job_lifecycle(self):
        response = self.client.post(
            "/jobs",
            json={
                "job_type": "predict_all",
                "payload": {"scenario_file": "scenario_03_equipment_failure.json"},
            },
        )
        self.assertEqual(response.status_code, 202)
        accepted = response.json()
        self.assertTrue(accepted["job_id"].startswith("job_"))
        self.assertIn(accepted["status"], {"QUEUED", "RUNNING", "COMPLETED", "FAILED"})

        result = self.client.get(f"/jobs/{accepted['job_id']}")
        self.assertEqual(result.status_code, 200)
        body = result.json()
        self.assertIn(body["status"], {"QUEUED", "RUNNING", "COMPLETED", "FAILED"})
        self.assertEqual(body["job_type"], "predict_all")
        if body["status"] == "COMPLETED":
            self.assertIsNotNone(body["result"])

    def test_unknown_job_is_404(self):
        response = self.client.get("/jobs/job_does_not_exist")
        self.assertEqual(response.status_code, 404)
