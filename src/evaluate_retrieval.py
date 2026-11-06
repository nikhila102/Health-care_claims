"""Small authored synthetic evaluation; not an independent real-world benchmark."""
import argparse
from functools import partial
import json
from src.retrieve_demo import retrieve

CASES = (
    ("Which documents support an appeal?", {"demo-appeal"}),
    ("Where is my claim status reference?", {"demo-status"}),
    ("What receipt is needed for reimbursement?", {"demo-receipt"}),
    ("How can I track a submission?", {"demo-status"}),
    ("astronomy telescope", set()),
    ("Does the policy cover dental implants?", set()),
)

# Authored after the common-term filter was frozen.
CHALLENGE_CASES = (
    ("Can I check status with a reference?", {"demo-status"}),
    ("Is an itemized receipt mandatory?", {"demo-receipt"}),
    ("Do I need a denial notice to appeal?", {"demo-appeal"}),
    ("How far along is my submission?", {"demo-status"}),
    ("What paperwork helps me contest a rejection?", {"demo-appeal"}),
    ("What proof of purchase do I need to get paid back?", {"demo-receipt"}),
    ("Does the policy cover orthodontics?", set()),
    ("Can I appeal a parking ticket?", set()),
    ("What is the maximum reimbursement amount?", set()),
    ("Is a claim reference needed for a password reset?", set()),
)

def evaluate_cases(cases, search=retrieve, k=2):
    if not cases:
        raise ValueError("cases must not be empty")
    positive, negative, recalls, reciprocal, abstentions = 0, 0, [], [], []
    details = []
    for query, relevant in cases:
        ids = [row["id"] for row in search(query, k=k)][:k]
        if relevant:
            positive += 1
            recalls.append(len(set(ids) & relevant) / len(relevant))
            reciprocal.append(next((1 / rank for rank, doc in enumerate(ids, 1) if doc in relevant), 0))
        else:
            negative += 1
            abstentions.append(float(not ids))
        details.append({"query": query, "relevant_ids": sorted(relevant), "retrieved_ids": ids})
    return {"synthetic_only": True, "k": k, "answerable_cases": positive,
            "unanswerable_cases": negative,
            "recall_at_k": sum(recalls)/positive if positive else None,
            "mrr_at_k": sum(reciprocal)/positive if positive else None,
            "unanswerable_abstention_rate": sum(abstentions)/negative if negative else None,
            "cases": details}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument('--split', choices=('development', 'challenge'), default='development')
    args = parser.parse_args()
    cases = CASES if args.split == 'development' else CHALLENGE_CASES
    report = evaluate_cases(cases)
    if args.compare:
        report = {"baseline": report, "filtered": evaluate_cases(
            cases, search=partial(retrieve, ignore_common=True))}
    print(json.dumps(report, indent=2))
