"""Compare the claims workflow with a source-specific intent check.

Run from the repository root: python -m src.evaluate_intent
Requires only Python and uses fictional examples authored for this diagnostic.
"""
import argparse
import json

from src.claims_workflow import route_question
from src.retrieve_demo import tokens

# Each candidate must match both a topic and a corresponding action or object.
INTENT_TERMS = {
    "demo-appeal": ({"appeal", "appeals"}, {"notice", "documents", "paperwork"}),
    "demo-status": ({"status", "track", "tracking"}, {"claim", "reference"}),
    "demo-receipt": ({"reimbursement", "reimburse"}, {"receipt", "receipts"}),
}

CASES = (
    ("What paperwork accompanies an appeal of a denial?", "demo-appeal"),
    ("Can I appeal the denial?", "demo-appeal"),
    ("Track my claim using its reference", "demo-status"),
    ("Is a receipt needed for reimbursement?", "demo-receipt"),
    ("Where should I mail the denial notice?", None),
    ("How do I replace a lost itemized receipt?", None),
    ("How do I dispute my claim status with a different provider?", None),
)


# Authored after the intent rules were fixed. Labels refer only to fictional passages.
PARAPHRASE_CASES = (
    ("What should accompany my denial appeal?", "demo-appeal"),
    ("Which documents do I need when appealing a denial?", "demo-appeal"),
    ("How can I track a submitted claim?", "demo-status"),
    ("Which reference lets me check claim status?", "demo-status"),
    ("What proof of payment does reimbursement require?", "demo-receipt"),
    ("Do I need an itemized receipt to be reimbursed?", "demo-receipt"),
    ("How long does an appeal take after I submit documents?", None),
    ("Can you change the status of my claim using its reference?", None),
    ("Can an itemized receipt guarantee reimbursement?", None),
)


def evaluate_intent(split="original"):
    splits = {"original": CASES, "paraphrases": PARAPHRASE_CASES}
    if split not in splits:
        raise ValueError(f"Unknown split: {split}")
    cases = []
    for query, expected in splits[split]:
        response = route_question(query, scope="demo-policy")
        baseline = [citation["source_id"] for citation in response["citations"]]
        words = set(tokens(query))
        filtered = [
            source for source in baseline
            if source in INTENT_TERMS and all(words & terms for terms in INTENT_TERMS[source])
        ]
        cases.append({
            "query": query, "expected_source": expected,
            "baseline": baseline, "intent_check": filtered,
        })

    return {
        "synthetic_only": True,
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
            for mode in ("baseline", "intent_check")
        },
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("original", "paraphrases"), default="original")
    args = parser.parse_args()
    print(json.dumps(evaluate_intent(args.split), indent=2))
