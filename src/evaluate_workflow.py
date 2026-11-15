"""Compare claims routing under verified, external, and unknown policy scope.

Run from the repository root: python -m src.evaluate_workflow
Requires only Python. Uses authored fictional cases from the intent-pair audit.
"""
import json

from src.claims_workflow import route_question
from src.evaluate_responses import INTENT_PAIRS


def evaluate_workflow():
    rows = []
    for scope in ("demo-policy", "external", "unknown"):
        for query, relevant_ids in INTENT_PAIRS:
            expected_ids = sorted(relevant_ids) if scope == "demo-policy" else []
            result = route_question(query, scope=scope)
            cited_ids = [citation["source_id"] for citation in result["citations"]]
            rows.append({
                "query": query,
                "scope": scope,
                "expected_source_ids": expected_ids,
                "cited_source_ids": cited_ids,
                "route": result["route"],
                "reason": result["reason"],
            })

    unsupported = [row for row in rows if not row["expected_source_ids"]]
    supported = [row for row in rows if row["expected_source_ids"]]
    return {
        "synthetic_only": True,
        "supported_cases": len(supported),
        "supported_with_relevant_citation": sum(
            bool(set(row["expected_source_ids"]).intersection(row["cited_source_ids"]))
            for row in supported
        ),
        "unsupported_cases_by_scope": {
            scope: {
                "cases": sum(row["scope"] == scope for row in unsupported),
                "with_citations": sum(
                    row["scope"] == scope and bool(row["cited_source_ids"])
                    for row in unsupported
                ),
            }
            for scope in ("demo-policy", "external", "unknown")
        },
        "cases": rows,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_workflow(), indent=2))
