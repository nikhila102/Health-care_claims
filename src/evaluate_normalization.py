"""Compare optional vocabulary normalization on authored synthetic paraphrases.

Run from the repository root: python -m src.evaluate_normalization
Uses Python's standard library. The 0.4 cutoff matches the evidence workflow.
Aliases were informed by these cases, so this is a development diagnostic.
"""
import json

from src.evaluate_intent import PARAPHRASE_CASES
from src.retrieve_demo import retrieve


def evaluate_normalization():
    cases = []
    for query, expected in PARAPHRASE_CASES:
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
    print(json.dumps(evaluate_normalization(), indent=2))
