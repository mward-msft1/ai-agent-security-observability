import argparse
import json
import logging
import os
import sys
import urllib.parse
from pathlib import Path

from . import collect, export
from .http import ApiError, Client, token_provider
from .store import Store, normalize


def parser():
    root = argparse.ArgumentParser(description="Agent security reference: docs/quickstart.md")
    root.add_argument("--db", default=".local/events.sqlite")
    root.add_argument("--auth", choices=("environment", "cli", "workload"), default="environment")
    root.add_argument("--include-content", action="store_true",
                      help="Store complete raw records, including sensitive content; requires approval environment flag")
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("graph", "audit", "management", "hunting", "transcripts"):
        command = sub.add_parser(name)
        command.add_argument("--start", required=True)
        command.add_argument("--end", required=True)
        if name == "graph":
            command.add_argument("--profile", choices=(*collect.PROFILES, "interactions"), required=True)
            command.add_argument("--user")
            command.add_argument("--allow-beta", action="store_true")
        elif name == "audit":
            command.add_argument("--operation", default="CopilotInteraction")
        elif name == "management":
            command.add_argument("--tenant", required=True)
            command.add_argument("--content-type", choices=("Audit.General", "Audit.AzureActiveDirectory",
                                "Audit.Exchange", "Audit.SharePoint", "DLP.All"), default="Audit.General")
        elif name == "hunting":
            command.add_argument("--query", required=True, type=Path)
        else:
            command.add_argument("--environment", required=True,
                                 help="Approved Dataverse HTTPS origin from Power Platform admin center")
    start = sub.add_parser("management-start")
    start.add_argument("--tenant", required=True)
    start.add_argument("--content-type", default="Audit.General", choices=(
        "Audit.General", "Audit.AzureActiveDirectory", "Audit.Exchange", "Audit.SharePoint", "DLP.All"))
    fixture = sub.add_parser("fixture")
    fixture.add_argument("--file", type=Path, default=Path("fixtures/audit.json"))
    output = sub.add_parser("export")
    output.add_argument("--file", type=Path, required=True)
    send = sub.add_parser("send")
    send.add_argument("--url", required=True)
    send.add_argument("--host", required=True, help="Explicit approved sink hostname")
    send.add_argument("--mode", choices=("sentinel", "generic", "splunk"), required=True)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.include_content and os.environ.get("CONTENT_CAPTURE_APPROVED") != "true":
        raise SystemExit("Content capture disabled; requires CONTENT_CAPTURE_APPROVED=true after governance review")
    store = Store(args.db)
    try:
        if args.command == "fixture":
            records = json.loads(args.file.read_text(encoding="utf-8"))
            store.save("synthetic-fixture", [normalize("synthetic-audit", r,
                        include_content=args.include_content) for r in records])
        elif args.command == "export":
            export.jsonl(store, args.file)
        elif args.command == "send":
            resource = "https://monitor.azure.com" if args.mode == "sentinel" else None
            if not resource and args.auth != "environment":
                raise ValueError("Third-party sink uses ACCESS_TOKEN from approved secret provider")
            token = token_provider(resource, args.auth)
            client = Client(token, [args.host])
            if args.mode == "splunk":
                # Splunk uses a different authorization scheme.
                original = client.request
                def hec(method, url, body=None, headers=None, retry=False):
                    return original(method, url, body,
                                    {**(headers or {}), "Authorization": "Splunk " + token()}, retry)
                client.request = hec
            export.send(store, client, args.url, args.mode)
        elif args.command == "transcripts":
            host = urllib.parse.urlsplit(args.environment).hostname
            client = Client(token_provider(args.environment.rstrip("/"), args.auth), [host])
            collect.transcripts(client, store, args.environment, args.start, args.end, args.include_content)
        else:
            management = args.command.startswith("management")
            resource = collect.MANAGEMENT if management else collect.GRAPH
            client = Client(token_provider(resource, args.auth),
                            ["manage.office.com"] if management else ["graph.microsoft.com"])
            if args.command == "graph":
                url = collect.graph_url(args.profile, args.start, args.end, args.user, args.allow_beta)
                collect.pages(client, store, url, args.profile, args.user or "", args.include_content)
            elif args.command == "audit":
                collect.audit_search(client, store, args.start, args.end, args.operation, args.include_content)
            elif args.command == "management":
                collect.management(client, store, args.tenant, args.start, args.end,
                                   args.content_type, args.include_content)
            elif args.command == "management-start":
                tenant = urllib.parse.quote(args.tenant, safe="")
                url = collect.query_url(f"{resource}/api/v1.0/{tenant}/activity/feed/subscriptions/start",
                                        {"contentType": args.content_type})
                client.request("POST", url)
            else:
                collect.hunting(client, store, args.query.read_text(encoding="utf-8"),
                                args.start, args.end, args.include_content)
    except (ApiError, ValueError, RuntimeError, TimeoutError, OSError) as error:
        logging.error("%s", error)
        return 1
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
