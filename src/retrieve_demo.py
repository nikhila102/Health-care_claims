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

COMMON_TERMS = frozenset('a an and the is are my how can which what where does policy fictional requires'.split())

# Explicit aliases for the fictional demo vocabulary.
TOKEN_ALIASES = {
    "appealing": "appeal", "appeals": "appeal",
    "reimbursed": "reimbursement", "reimburse": "reimbursement",
    "receipts": "receipt", "require": "requires",
}


def retrieve(query, k=2, *, ignore_common=False, normalize_terms=False):
    """Return positive cosine matches with stable IDs; abstain on no overlap."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be nonempty text")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    excluded = COMMON_TERMS if ignore_common else frozenset()
    def vector(text):
        words = tokens(text)
        if normalize_terms:
            words = [TOKEN_ALIASES.get(word, word) for word in words]
        return Counter(word for word in words if word not in excluded)

    q = vector(query)
    results = []
    for document in DOCUMENTS:
        d = vector(document["text"])
        dot = sum(value*d[word] for word, value in q.items())
        if dot:
            score = dot / ((sum(v*v for v in q.values()) * sum(v*v for v in d.values())) ** 0.5)
            results.append({**document, "score": score})
    return sorted(results, key=lambda row: (-row["score"], row["id"]))[:k]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--ignore-common", action="store_true", help="Ignore common and boilerplate terms")
    parser.add_argument("--normalize-terms", action="store_true", help="Normalize explicit demo vocabulary aliases")
    args = parser.parse_args()
    print(json.dumps({"synthetic_only": True, "matches": retrieve(args.query, ignore_common=args.ignore_common, normalize_terms=args.normalize_terms)}, indent=2))
