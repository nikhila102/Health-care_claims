import json
import subprocess
import sys
import unittest
from src.evidence_response import evidence_response
from src.retrieve_demo import DOCUMENTS

class EvidenceTests(unittest.TestCase):
    def test_citations_are_exact_source_quotes(self):
        response = evidence_response("appeal denial")
        sources = {row["id"]: row["text"] for row in DOCUMENTS}
        self.assertEqual(response["status"], "evidence_found")
        self.assertTrue(response["citations"])
        for citation in response["citations"]:
            self.assertEqual(citation["quote"], sources[citation["source_id"]])

    def test_empty_result_has_no_citations(self):
        response = evidence_response("astronomy telescope")
        self.assertEqual(response["status"], "no_evidence")
        self.assertEqual(response["citations"], [])

    def test_cli_emits_json_and_rejects_invalid_k(self):
        output = subprocess.check_output([sys.executable, "-m", "src.evidence_response", "itemized receipt"])
        self.assertEqual(json.loads(output)["citations"][0]["source_id"], "demo-receipt")
        invalid = subprocess.run([sys.executable, "-m", "src.evidence_response", "receipt", "--k", "0"], capture_output=True)
        self.assertEqual(invalid.returncode, 2)
