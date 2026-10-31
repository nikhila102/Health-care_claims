import unittest
from src.evaluate_synthetic import evaluate

class EvaluationTests(unittest.TestCase):
    def test_reproducible_disjoint_holdout_and_baseline(self):
        result = evaluate()
        self.assertEqual(result, evaluate())
        train, test = set(result["train_indices"]), set(result["test_indices"])
        self.assertFalse(train & test)
        self.assertEqual(len(train | test), 500)
        self.assertEqual(result["test_rows"], 100)
        for metric in ("mae", "rmse"):
            self.assertLess(result["metrics"]["linear_regression"][metric],
                            result["metrics"]["mean_baseline"][metric])

if __name__ == "__main__":
    unittest.main()
