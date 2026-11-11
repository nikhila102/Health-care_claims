import unittest
from src.evidence_response import evidence_response

class MinimumScoreTests(unittest.TestCase):
    def test_threshold_includes_boundary_and_rejects_higher_cutoff(self):
        query = "appeal denial"
        score = evidence_response(query)["citations"][0]["retrieval_score"]
        self.assertEqual(evidence_response(query, min_score=score)["status"], "evidence_found")
        self.assertEqual(evidence_response(query, min_score=1)["status"], "no_evidence")

    def test_invalid_thresholds(self):
        for value in (-1, 2, float("nan"), float("inf"), True, "0.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evidence_response("appeal", min_score=value)
