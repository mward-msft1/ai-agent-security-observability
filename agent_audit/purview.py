"""Fail-closed text policy probe, not a full enterprise policy engine.

Sources: [P1-P4] in docs/sources.md. No model or delivery is invoked here.
"""

import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from .collect import GRAPH


class PolicyBlocked(RuntimeError):
    pass


def check_actions(actions):
    if not isinstance(actions, list):
        raise PolicyBlocked("Missing policyActions array")
    for action in actions:
        if action.get("action") == "restrictAccess":
            raise PolicyBlocked("Purview restrictAccess action; stop before model/tool/delivery")
        raise PolicyBlocked("Unimplemented policy action; manual review required")


def content_body(app, activity, correlation, sequence, text=None):
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "@odata.type": "microsoft.graph.processConversationMetadata",
        "identifier": str(uuid.uuid4()), "name": "Synthetic reference interaction",
        "correlationId": correlation, "sequenceNumber": sequence, "isTruncated": False,
        "createdDateTime": now, "modifiedDateTime": now,
    }
    if text is not None:
        entry["content"] = {"@odata.type": "microsoft.graph.textContent", "data": text}
    return {"contentToProcess": {
        "contentEntries": [entry], "activityMetadata": {"activity": activity},
        "protectedAppMetadata": {
            "name": "Agent security reference", "version": "0.1.0",
            "applicationLocation": {
                "@odata.type": "microsoft.graph.policyLocationApplication", "value": app}},
        "integratedAppMetadata": {"name": "Agent security reference", "version": "0.1.0"},
    }}


def probe(client, user, app, activity, text, correlation, sequence):
    if activity not in ("uploadText", "downloadText"):
        raise ValueError("This example supports text only")
    root = f"{GRAPH}/v1.0/users/{quote(user, safe='')}/dataSecurityAndGovernance"
    compute = {"activities": activity, "locations": [
        {"@odata.type": "microsoft.graph.policyLocationApplication", "value": app}]}
    for _ in range(2):
        scopes, headers, _ = client.request("POST", root + "/protectionScopes/compute", compute)
        if not isinstance(scopes, dict) or not isinstance(scopes.get("value"), list):
            raise PolicyBlocked("Invalid protection scope response")
        etag = next((v for k, v in headers.items() if k.lower() == "etag"), None)
        applicable = []
        for scope in scopes["value"]:
            activities = scope.get("activities", "")
            if not isinstance(activities, str):
                raise PolicyBlocked("Unexpected activities schema")
            if activity in [a.strip() for a in activities.split(",")]:
                check_actions(scope.get("policyActions"))
                applicable.append(scope)
        if not applicable:
            client.request("POST", root + "/activities/contentActivities",
                           content_body(app, activity, correlation, sequence))
            return "metadata-only-no-applicable-policy"
        modes = {scope.get("executionMode") for scope in applicable}
        if not modes <= {"evaluateInline", "evaluateOffline"} or not etag:
            raise PolicyBlocked("Unknown execution mode or absent policy ETag")
        result, _, status = client.request(
            "POST", root + "/processContent",
            content_body(app, activity, correlation, sequence, text),
            {"If-None-Match": etag, "Client-Request-Id": str(uuid.uuid4())})
        if status in (202, 204):
            if "evaluateInline" in modes:
                raise PolicyBlocked("Inline policy did not return an evaluation decision")
            return "submitted-offline-not-an-enforcement-verdict"
        if not isinstance(result, dict):
            raise PolicyBlocked("Missing content evaluation response")
        if result.get("processingErrors") != []:
            raise PolicyBlocked("Processing errors or missing error array")
        check_actions(result.get("policyActions"))
        state = result.get("protectionScopeState")
        if state == "modified":
            continue
        if state != "notModified":
            raise PolicyBlocked("Unknown policy state")
        return "evaluated-inline-no-actions" if "evaluateInline" in modes else "submitted-offline-not-an-enforcement-verdict"
    raise PolicyBlocked("Policies changed repeatedly; retry after administrative review")
