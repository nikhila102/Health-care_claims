import unittest
from src.evaluate_retrieval import evaluate_cases

class CutoffTests(unittest.TestCase):
    def test_invalid_cutoffs_rejected_before_search(self):
        def search(*args, **kwargs):
            self.fail("invalid cutoff must be rejected before retrieval")
        for cutoff in (0, -1, True, 1.5, None):
            with self.subTest(cutoff=cutoff):
                with self.assertRaises(ValueError):
                    evaluate_cases([("query", {"right"})], search, k=cutoff)

    def test_rank_cutoff_changes_metrics(self):
        def search(query, k):
            return [{"id": "wrong"}, {"id": "right"}]
        cases = [("query", {"right"})]
        first = evaluate_cases(cases, search, k=1)
        second = evaluate_cases(cases, search, k=2)
        self.assertEqual(first["recall_at_k"], 0)
        self.assertEqual(first["mrr_at_k"], 0)
        self.assertEqual(second["recall_at_k"], 1)
        self.assertEqual(second["mrr_at_k"], 0.5)
