"""Offline routing regression tests.

Run from the repository root: python -m unittest discover -s tests -p test_claims_workflow.py -v
"""
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from src.claims_workflow import route_question
from src.retrieve_demo import DOCUMENTS


class ClaimsWorkflowTests(unittest.TestCase):
    def test_scope_gate_bypasses_retrieval_even_for_strong_matches(self):
        with patch("src.claims_workflow.evidence_response") as retrieve:
            for scope, reason in (("unknown", "scope_unverified"),
                                  ("external", "external_policy")):
                with self.subTest(scope=scope):
                    result = route_question("appeal denial", scope=scope)
                    self.assertEqual(result["route"], "human_review")
                    self.assertEqual(result["reason"], reason)
                    self.assertEqual(result["citations"], [])
            retrieve.assert_not_called()

    def test_demo_policy_cites_exact_passage(self):
        result = route_question("appeal denial", scope="demo-policy")
        source = next(doc for doc in DOCUMENTS if doc["id"] == "demo-appeal")
        self.assertEqual(result["route"], "evidence_review")
        self.assertEqual(result["reason"], "candidate_evidence")
        citation = result["citations"][0]
        self.assertEqual(citation["source_id"], source["id"])
        self.assertEqual(citation["quote"], source["text"])

    def test_demo_policy_escalates_when_score_is_too_low(self):
        result = route_question("appeal school suspension", scope="demo-policy")
        self.assertEqual(result["route"], "human_review")
        self.assertEqual(result["reason"], "no_evidence")
        self.assertEqual(result["citations"], [])

    def test_cli_defaults_to_unverified_scope(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.claims_workflow", "appeal denial"],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertIs(payload["synthetic_only"], True)
        self.assertEqual(payload["scope"], "unknown")
        self.assertEqual(payload["reason"], "scope_unverified")

    def test_external_insurer_question_requires_verified_scope(self):
        query = "Can receipts from another insurer be reimbursed?"
        for scope, reason in (("external", "external_policy"),
                              ("unknown", "scope_unverified")):
            with self.subTest(scope=scope), patch(
                "src.claims_workflow.evidence_response",
                side_effect=AssertionError("Retrieval must be skipped"),
            ):
                result = route_question(query, scope=scope)
                self.assertEqual(result["route"], "human_review")
                self.assertEqual(result["reason"], reason)
                self.assertEqual(result["citations"], [])

    def test_invalid_requests_fail_before_retrieval(self):
        requests = [
            (None, "demo-policy"), (42, "demo-policy"),
            ("", "demo-policy"), ("  ", "external"),
            ("appeal denial", "unrecognized"),
        ]
        with patch("src.claims_workflow.evidence_response") as retrieve:
            for query, scope in requests:
                with self.subTest(query=query, scope=scope):
                    with self.assertRaises(ValueError):
                        route_question(query, scope=scope)
            retrieve.assert_not_called()

    def test_cli_rejects_invalid_scope_without_json_response(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.claims_workflow", "appeal denial",
             "--scope", "unrecognized"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid choice", result.stderr)
