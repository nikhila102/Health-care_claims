"""Check evaluation accounting with controlled fictional retrieval outcomes.

Run: python -m unittest discover -s tests -p test_intent_evaluation.py -v
"""
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from src.evaluate_intent import evaluate_intent


class IntentEvaluationTests(unittest.TestCase):
    def test_metrics_count_relevance_instead_of_any_citation(self):
        cases = (
            ("appeal documents", "demo-appeal"),
            ("claim status", "demo-status"),
            ("reimbursement receipt", None),
        )
        outcomes = [
            {"citations": [{"source_id": "demo-status"}]},
            {"citations": [{"source_id": "demo-status"}]},
            {"citations": [{"source_id": "demo-receipt"}]},
        ]
        with patch("src.evaluate_intent.CASES", cases), patch(
            "src.evaluate_intent.route_question", side_effect=outcomes
        ):
            report = evaluate_intent()
        self.assertEqual(report["supported_cases"], 2)
        self.assertEqual(report["unsupported_cases"], 1)
        for mode in ("baseline", "intent_check"):
            self.assertEqual(report["metrics"][mode], {
                "supported_with_relevant_citation": 1,
                "unsupported_with_citation": 1,
            })

    def test_empty_retrieval_stays_empty(self):
        with patch("src.evaluate_intent.route_question", return_value={"citations": []}):
            report = evaluate_intent()
        for row in report["cases"]:
            self.assertEqual(row["intent_check"], [])
        for metrics in report["metrics"].values():
            self.assertEqual(metrics["supported_with_relevant_citation"], 0)
            self.assertEqual(metrics["unsupported_with_citation"], 0)

    def test_cli_matches_repeatable_api_report(self):
        output = subprocess.run(
            [sys.executable, "-m", "src.evaluate_intent"],
            check=True, text=True, capture_output=True,
        )
        report = evaluate_intent()
        self.assertEqual(json.loads(output.stdout), report)
        self.assertEqual(evaluate_intent(), report)
