"""Synthetic, explicitly opt-in Purview API evaluation. Sources: [P1-P4]."""

import argparse
import os
import uuid

from agent_audit.http import Client, token_provider
from agent_audit.purview import probe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--user", required=True)
    parser.add_argument("--app", required=True)
    args = parser.parse_args()
    if not args.live or os.environ.get("CONTENT_CAPTURE_APPROVED") != "true":
        raise SystemExit("No requests sent. --live and CONTENT_CAPTURE_APPROVED=true required.")
    client = Client(token_provider("https://graph.microsoft.com"), ["graph.microsoft.com"])
    correlation = str(uuid.uuid4())
    for sequence, (activity, text) in enumerate((
        ("uploadText", "Summarize synthetic document EXAMPLE-ONLY."),
        ("downloadText", "The synthetic document contains no real customer data."),
    )):
        print(activity, probe(client, args.user, args.app, activity, text, correlation, sequence))
    print("Probe only; no model, tool, or delivery invoked. Inspect Purview separately.")


if __name__ == "__main__":
    main()
