import unittest
from src.retrieve_demo import retrieve

class RetrievalTests(unittest.TestCase):
    def test_known_questions_return_expected_evidence(self):
        for query, expected in [("appeal denial", "demo-appeal"), ("claim status", "demo-status"), ("itemized receipt", "demo-receipt")]:
            with self.subTest(query=query):
                self.assertEqual(retrieve(query)[0]["id"], expected)

    def test_unknown_query_abstains(self):
        self.assertEqual(retrieve("astronomy telescope"), [])

    def test_invalid_inputs(self):
        for query in ("", " ", None):
            with self.assertRaises(ValueError):
                retrieve(query)
        for k in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                retrieve("appeal", k)

    def test_limit_and_determinism(self):
        self.assertEqual(len(retrieve("fictional policy", 1)), 1)
        self.assertEqual(retrieve("fictional policy"), retrieve("fictional policy"))
