import unittest

from pipelines.preprocessing.moil_reference import validate

class TestMoilPreprocessing(unittest.TestCase):
    def test_canonical_reference_exports_validate(self):
        result = validate()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["site_rows"], 10)
        self.assertEqual(result["grade_rows"], 10)
        self.assertEqual(result["production_rows"], 10)
