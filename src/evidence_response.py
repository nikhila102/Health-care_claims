"""Structured evidence selection over fictional passages."""
import argparse
import json
import math
from src.retrieve_demo import retrieve

def evidence_response(query, k=2, *, min_score=0.0):
    if (isinstance(min_score, bool) or not isinstance(min_score, (int, float))
            or not 0 <= min_score <= 1 or not math.isfinite(min_score)):
        raise ValueError('min_score must be a finite number between 0 and 1')
    matches = retrieve(query, k=k, ignore_common=True)
    matches = [match for match in matches if match['score'] >= min_score]
    return {
        "schema_version": 1,
        "synthetic_only": True,
        "status": "evidence_found" if matches else "no_evidence",
        "query": query,
        "citations": [
            {"source_id": match["id"], "quote": match["text"], "retrieval_score": match["score"]}
            for match in matches
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument('--min-score', type=float, default=0.0)
    args = parser.parse_args()
    try:
        response = evidence_response(args.query, args.k, min_score=args.min_score)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(response, indent=2, allow_nan=False))

if __name__ == "__main__":
    main()
