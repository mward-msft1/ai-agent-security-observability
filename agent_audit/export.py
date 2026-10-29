"""Explicit-write exports with durable per-destination acknowledgement."""

import json
from pathlib import Path

from .store import digest


def jsonl(store, path):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        for record in store.events():
            output.write(json.dumps(record, sort_keys=True) + "\n")
    temporary.replace(target)


def send(store, client, url, mode="generic"):
    client.check_url(url)
    destination = digest([mode, url])
    for identifier, record in store.pending(destination):
        headers = {}
        if mode == "sentinel":
            body = [record]
        elif mode == "splunk":
            body = {"sourcetype": "_json", "event": record}
        else:
            body = record
            headers["Idempotency-Key"] = identifier
        if len(json.dumps(body).encode("utf-8")) > 900000:
            raise ValueError("Event exceeds 900,000-byte safety limit; no truncation or acknowledgement")
        response, _, status = client.request("POST", url, body, headers, retry=True)
        if status == 202:
            raise RuntimeError("Asynchronous sink acceptance requires a receipt verifier; not acknowledged")
        if mode == "splunk" and (not isinstance(response, dict) or response.get("code") != 0):
            raise RuntimeError("Splunk HEC did not accept event; not acknowledged")
        store.acknowledge(destination, [identifier])
