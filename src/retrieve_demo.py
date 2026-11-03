"""Offline lexical retrieval demo over invented policy text, not real coverage rules."""
import json
import re
from collections import Counter

DOCUMENTS = (
    {"id": "demo-appeal", "text": "Fictional policy: an appeal requires a denial notice and supporting documents."},
    {"id": "demo-status", "text": "Fictional policy: check claim status using the claim reference."},
    {"id": "demo-receipt", "text": "Fictional policy: reimbursement requires an itemized receipt."},
)

def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())

def retrieve(query, k=2):
    """Return positive cosine matches with stable IDs; abstain on no overlap."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be nonempty text")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    q = Counter(tokens(query))
    results = []
    for document in DOCUMENTS:
        d = Counter(tokens(document["text"]))
        dot = sum(value*d[word] for word, value in q.items())
        if dot:
            score = dot / ((sum(v*v for v in q.values()) * sum(v*v for v in d.values())) ** 0.5)
            results.append({**document, "score": score})
    return sorted(results, key=lambda row: (-row["score"], row["id"]))[:k]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    args = parser.parse_args()
    print(json.dumps({"synthetic_only": True, "matches": retrieve(args.query)}, indent=2))
