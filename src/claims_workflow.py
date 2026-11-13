"""Route fictional claims questions to cited evidence or human review.

Run from the repository root with Python 3.10+ and no extra dependencies:
    python -m src.claims_workflow "appeal denial" --scope demo-policy
    python -m src.claims_workflow "appeal denial" --scope external

Scope is supplied by the caller from trusted routing metadata. The workflow
does not infer policy ownership or intent from question text.
"""
import argparse
import json

from src.evidence_response import evidence_response


def route_question(query: str, *, scope: str = "unknown") -> dict:
    """Return a review decision without making a coverage determination."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be nonempty text")
    if scope not in ("demo-policy", "external", "unknown"):
        raise ValueError("invalid policy scope")

    result = {
        "schema_version": 1,
        "synthetic_only": True,
        "scope": scope,
        "route": "human_review",
        "reason": "scope_unverified",
        "citations": [],
    }
    if scope == "external":
        result["reason"] = "external_policy"
    if scope != "demo-policy":
        return result

    evidence = evidence_response(query, min_score=0.4)
    result["citations"] = evidence["citations"]
    result["reason"] = "no_evidence"
    if result["citations"]:
        result.update(route="evidence_review", reason="candidate_evidence")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--scope", choices=("demo-policy", "external", "unknown"),
                        default="unknown")
    args = parser.parse_args()
    try:
        result = route_question(args.query, scope=args.scope)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
