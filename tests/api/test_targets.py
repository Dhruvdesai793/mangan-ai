import unittest

from services.api.schemas.requests import CoordinatePredictionRequest


class TestCoordinateTargetContract(unittest.TestCase):
    def test_coordinate_request_defaults_to_a_safe_buffer(self):
        request = CoordinatePredictionRequest(latitude=21.855, longitude=80.231389)
        self.assertEqual(request.buffer_m, 250)

    def test_coordinate_request_rejects_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            CoordinatePredictionRequest(latitude=91, longitude=80)
