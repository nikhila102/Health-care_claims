"""Compare optional vocabulary normalization on authored synthetic paraphrases.

Run from the repository root: python -m src.evaluate_normalization
Uses Python's standard library. The 0.4 cutoff matches the evidence workflow.
Aliases were informed by these cases, so this is a development diagnostic.
"""
import argparse
import json

from src.evaluate_intent import PARAPHRASE_CASES
from src.retrieve_demo import retrieve


# Written after TOKEN_ALIASES was fixed. These are authored diagnostics.
FRESH_CASES = (
    ("Appeals require which supporting documents?", "demo-appeal"),
    ("For reimbursement, are receipts required?", "demo-receipt"),
    ("Can I check the claim status by reference?", "demo-status"),
    ("What must I attach when appealing?", "demo-appeal"),
    ("Will appealing guarantee approval?", None),
    ("How many days until I am reimbursed?", None),
    ("Can receipts from another insurer be reimbursed?", None),
    ("Can the claim reference reveal my doctor's address?", None),
)


def evaluate_normalization(split="development"):
    splits = {"development": PARAPHRASE_CASES, "fresh": FRESH_CASES}
    if split not in splits:
        raise ValueError(f"Unknown split: {split}")
    cases = []
    for query, expected in splits[split]:
        row = {"query": query, "expected_source": expected}
        for mode, enabled in (("baseline", False), ("normalized", True)):
            matches = retrieve(query, ignore_common=True, normalize_terms=enabled)
            row[mode] = [
                match["id"] for match in matches if match["score"] >= 0.4
            ]
        cases.append(row)
    return {
        "synthetic_only": True,
        "min_score": 0.4,
        "supported_cases": sum(row["expected_source"] is not None for row in cases),
        "unsupported_cases": sum(row["expected_source"] is None for row in cases),
        "metrics": {
            mode: {
                "supported_with_relevant_citation": sum(
                    row["expected_source"] in row[mode] for row in cases
                ),
                "unsupported_with_citation": sum(
                    row["expected_source"] is None and bool(row[mode]) for row in cases
                ),
            }
            for mode in ("baseline", "normalized")
        },
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("development", "fresh"), default="development")
    args = parser.parse_args()
    print(json.dumps(evaluate_normalization(args.split), indent=2))
