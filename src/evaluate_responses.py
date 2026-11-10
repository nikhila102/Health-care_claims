"""Evaluate evidence responses on authored synthetic challenge questions."""
import json
from src.evidence_response import evidence_response
from src.evaluate_retrieval import CHALLENGE_CASES, evaluate_cases
from src.retrieve_demo import DOCUMENTS

def evaluate_responses():
    sources = {document["id"]: document["text"] for document in DOCUMENTS}
    responses = {}
    def search(query, k):
        response = evidence_response(query, k)
        responses[query] = response
        return [{"id": citation["source_id"]} for citation in response["citations"]]
    report = evaluate_cases(CHALLENGE_CASES, search=search)
    citations = [citation for response in responses.values() for citation in response["citations"]]
    exact = sum(sources.get(citation["source_id"]) == citation["quote"] for citation in citations)
    report["citation_count"] = len(citations)
    report["exact_source_quote_rate"] = exact / len(citations) if citations else None
    report["responses"] = list(responses.values())
    return report

if __name__ == "__main__":
    print(json.dumps(evaluate_responses(), indent=2, allow_nan=False))
