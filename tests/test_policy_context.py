"""Integration tests for fictional policy metadata.

Run: python -m unittest discover -s tests -p test_policy_context.py -v
"""
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

from src.policy_context import route_with_policy
from src.retrieve_demo import DOCUMENTS


class PolicyContextTests(unittest.TestCase):
    def test_known_policy_returns_exact_source(self):
        response = route_with_policy("appeal denial", policy_id="demo-policy-v1")
        self.assertEqual(response["route"], "evidence_review")
        source = next(row for row in DOCUMENTS if row["id"] == "demo-appeal")
        self.assertEqual(response["citations"][0]["quote"], source["text"])

    def test_unknown_and_similar_ids_skip_retrieval(self):
        cases = (
            (None, "scope_unverified"),
            ("different-policy", "external_policy"),
            ("demo-policy-v1 ", "external_policy"),
            ("DEMO-POLICY-V1", "external_policy"),
        )
        with patch("src.claims_workflow.evidence_response") as retrieve:
            for policy_id, reason in cases:
                with self.subTest(policy_id=policy_id):
                    response = route_with_policy("appeal denial", policy_id=policy_id)
                    self.assertEqual(response["route"], "human_review")
                    self.assertEqual(response["reason"], reason)
                    self.assertEqual(response["citations"], [])
            retrieve.assert_not_called()

    def test_malformed_metadata_rejected_before_workflow(self):
        with patch("src.policy_context.route_question") as workflow:
            for invalid in ("", " ", 1, False, [], {}):
                with self.subTest(policy_id=invalid):
                    with self.assertRaises(ValueError):
                        route_with_policy("appeal denial", policy_id=invalid)
            workflow.assert_not_called()

    def test_cli_defaults_and_validation(self):
        command = [sys.executable, "-m", "src.policy_context", "appeal denial"]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["reason"], "scope_unverified")
        invalid = subprocess.run(
            command + ["--policy-id", ""], capture_output=True, text=True,
        )
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, "")
        self.assertIn("policy_id must be nonempty", invalid.stderr)
