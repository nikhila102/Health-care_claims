"""Structured evidence selection over fictional passages."""
import argparse
import json
from src.retrieve_demo import retrieve

def evidence_response(query, k=2):
    matches = retrieve(query, k=k, ignore_common=True)
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
    args = parser.parse_args()
    try:
        response = evidence_response(args.query, args.k)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(response, indent=2, allow_nan=False))

if __name__ == "__main__":
    main()
