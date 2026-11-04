import unittest
from src.evaluate_retrieval import evaluate_cases

class MetricTests(unittest.TestCase):
    def test_known_rank_and_abstention_metrics(self):
        def search(query, k):
            return [{"id": doc} for doc in {"positive": ["wrong", "right"], "negative": ["wrong"]}[query]]
        report = evaluate_cases([("positive", {"right", "missing"}), ("negative", set())], search)
        self.assertEqual(report["recall_at_k"], 0.5)
        self.assertEqual(report["mrr_at_k"], 0.5)
        self.assertEqual(report["unanswerable_abstention_rate"], 0)
    def test_no_positive_cases_and_correct_abstention(self):
        report = evaluate_cases([("unknown", set())], lambda query, k: [])
        self.assertIsNone(report["recall_at_k"])
        self.assertEqual(report["unanswerable_abstention_rate"], 1)
    def test_empty_cases_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_cases([])
