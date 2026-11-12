"""Evaluate evidence responses on authored synthetic challenge questions."""
import argparse
import json
from src.evidence_response import evidence_response
from src.evaluate_retrieval import CHALLENGE_CASES, evaluate_cases
from src.retrieve_demo import DOCUMENTS

# These pairs were authored after the 0.4 cutoff was selected.
INTENT_PAIRS = (
    ("What documents must accompany an appeal?", {"demo-appeal"}),
    ("What documents must accompany an appeal for a school suspension?", set()),
    ("Can I check claim status with a claim reference?", {"demo-status"}),
    ("Can I check claim status with a claim reference from another insurer?", set()),
    ("Does reimbursement require an itemized receipt?", {"demo-receipt"}),
    ("Does reimbursement require an itemized receipt for a business trip?", set()),
)

def evaluate_responses(*, min_score=0.0, split="challenge"):
    splits = {"challenge": CHALLENGE_CASES, "intent-pairs": INTENT_PAIRS}
    if split not in splits:
        raise ValueError(f"Unknown evaluation split: {split}")

    sources = {document["id"]: document["text"] for document in DOCUMENTS}
    responses = {}
    def search(query, k):
        response = evidence_response(query, k, min_score=min_score)
        responses[query] = response
        return [{"id": citation["source_id"]} for citation in response["citations"]]
    report = evaluate_cases(splits[split], search=search)
    citations = [citation for response in responses.values() for citation in response["citations"]]
    exact = sum(sources.get(citation["source_id"]) == citation["quote"] for citation in citations)
    report["split"] = split
    report["min_score"] = min_score
    report["citation_count"] = len(citations)
    report["exact_source_quote_rate"] = exact / len(citations) if citations else None
    report["responses"] = list(responses.values())
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-score", type=float, default=0.0)
    parser.add_argument("--split", choices=("challenge", "intent-pairs"), default="challenge")
    args = parser.parse_args()
    try:
        report = evaluate_responses(min_score=args.min_score, split=args.split)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, allow_nan=False))
