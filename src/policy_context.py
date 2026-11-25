"""Demonstrate claims routing from fictional application policy metadata.

Run from the repository root with Python 3.10+:
    python -m src.policy_context "appeal denial" --policy-id demo-policy-v1

In an application, policy_id must come from a verified server-side record.
The CLI accepts it directly for demonstration. It does not authenticate users.
Missing metadata routes to human review. Only the fictional ID below maps to
the demo corpus. Other nonempty IDs map to an external policy.
"""
import argparse
import json

from src.claims_workflow import route_question


def route_with_policy(query, *, policy_id=None):
    """Map application metadata to the existing workflow's policy scope."""
    if policy_id is not None and (
        not isinstance(policy_id, str) or not policy_id.strip()
    ):
        raise ValueError("policy_id must be nonempty text or None")
    scope = "unknown"
    if policy_id is not None:
        scope = "demo-policy" if policy_id == "demo-policy-v1" else "external"
    return route_question(query, scope=scope)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--policy-id")
    args = parser.parse_args()
    try:
        result = route_with_policy(args.query, policy_id=args.policy_id)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
