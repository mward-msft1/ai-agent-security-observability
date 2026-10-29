"""Documented commercial-cloud REST collection surfaces; see docs/permissions.md."""

import time
import urllib.parse
from datetime import datetime, timezone

from .store import digest, normalize

GRAPH = "https://graph.microsoft.com"
MANAGEMENT = "https://manage.office.com"
PROFILES = {
    "signins": ("v1.0/auditLogs/signIns", "createdDateTime"),
    "directory-audit": ("v1.0/auditLogs/directoryAudits", "activityDateTime"),
    "alerts": ("v1.0/security/alerts_v2", "createdDateTime"),
    "incidents": ("v1.0/security/incidents", "createdDateTime"),
    "service-principals": ("v1.0/servicePrincipals", None),
    "risky-agents": ("beta/identityProtection/riskyAgents", None),
    "agent-identities": ("beta/servicePrincipals/microsoft.graph.agentIdentity", None),
}


def window(start, end):
    first, last = (datetime.fromisoformat(x.replace("Z", "+00:00")) for x in (start, end))
    if first.tzinfo is None or last.tzinfo is None or first >= last:
        raise ValueError("Provide offset-aware UTC start < end")
    return first, last


def query_url(base, params):
    return base + "?" + urllib.parse.urlencode(params)


def graph_url(profile, start, end, user=None, beta=False):
    window(start, end)
    if profile == "interactions":
        if not user:
            raise ValueError("interactions requires the licensed user's object ID")
        path = f"v1.0/copilot/users/{urllib.parse.quote(user, safe='')}/interactionHistory/getAllEnterpriseInteractions"
        # Documented export filter uses both strict boundaries; overlap scheduled windows.
        return query_url(f"{GRAPH}/{path}", {
            "$filter": f"createdDateTime gt {start} and createdDateTime lt {end}", "$top": "100"})
    path, date = PROFILES[profile]
    if path.startswith("beta/") and not beta:
        raise ValueError("This profile is preview; pass --allow-beta after reviewing limitations")
    params = {}
    if date:
        params["$filter"] = f"{date} ge {start} and {date} lt {end}"
    if profile == "service-principals":
        params["$select"] = "id,appId,servicePrincipalType,accountEnabled"
    return query_url(f"{GRAPH}/{path}", params)


def pages(client, store, url, source, namespace="", include_content=False):
    job = digest([url, source, namespace, include_content])
    cursor = store.cursor(job)
    current = cursor["next"] if cursor else url
    visited = set()
    while current:
        if current in visited:
            raise RuntimeError("Pagination cycle detected; checkpoint retained")
        visited.add(current)
        page, _, _ = client.request("GET", current, retry=True)
        if not isinstance(page, dict) or not isinstance(page.get("value"), list):
            raise ValueError("Expected OData collection with value array")
        next_url = page.get("@odata.nextLink")
        if next_url:
            client.check_url(next_url)
        rows = [normalize(source, row, namespace, include_content) for row in page["value"]]
        store.save(job, rows, {"next": next_url} if next_url else None)
        current = next_url


def audit_search(client, store, start, end, operation="CopilotInteraction",
                 include_content=False, max_polls=60, sleep=time.sleep):
    window(start, end)
    body = {"displayName": "Agent security reference bounded search",
            "filterStartDateTime": start, "filterEndDateTime": end,
            "operationFilters": [operation]}
    job = digest(["audit-search", body, include_content])
    state = store.cursor(job)
    if not state:
        # No automatic retry: a lost response may have created a saved query.
        result, _, _ = client.request("POST", f"{GRAPH}/v1.0/security/auditLog/queries", body)
        state = {"id": result["id"]}
        store.save(job, [], state)
    query = f"{GRAPH}/v1.0/security/auditLog/queries/{urllib.parse.quote(state['id'], safe='')}"
    for _ in range(max_polls):
        result, _, _ = client.request("GET", query, retry=True)
        status = result["status"]
        if status == "succeeded":
            pages(client, store, query + "/records", "purview-audit",
                  include_content=include_content)
            store.save(job, [])
            return
        if status not in ("notStarted", "running"):
            raise RuntimeError(f"Audit search terminal/unrecognized status: {status}; query ID retained")
        sleep(10)
    raise TimeoutError("Audit search not complete; rerun same window to resume saved query")


def management(client, store, tenant, start, end, content_type="Audit.General",
               include_content=False, now=None):
    first, last = window(start, end)
    now = now or datetime.now(timezone.utc)
    if (last - first).total_seconds() > 86400 or (now - first).total_seconds() > 7 * 86400:
        raise ValueError("Management API requires <=24h window and start within last 7 days")
    if last > now:
        raise ValueError("Management content window must not be in the future")
    root = f"{MANAGEMENT}/api/v1.0/{urllib.parse.quote(tenant, safe='')}/activity/feed"
    initial = query_url(root + "/subscriptions/content", {
        "contentType": content_type, "startTime": start, "endTime": end})
    job = digest([initial, include_content])
    state = store.cursor(job)
    current = state["next"] if state else initial
    visited = set()
    while current:
        if current in visited:
            raise RuntimeError("Management pagination cycle detected")
        visited.add(current)
        blobs, headers, _ = client.request("GET", current, retry=True)
        if not isinstance(blobs, list):
            raise ValueError("Expected Management API content descriptor array")
        for blob in blobs:
            records, _, _ = client.request("GET", blob["contentUri"], retry=True)
            if not isinstance(records, list):
                raise ValueError("Expected Management API content array")
            store.save(job, [normalize("management-" + content_type, r, tenant, include_content)
                             for r in records], {"next": current})
        next_url = next((v for k, v in headers.items() if k.lower() == "nextpageuri"), None)
        if next_url:
            client.check_url(next_url)
        store.save(job, [], {"next": next_url} if next_url else None)
        current = next_url


def hunting(client, store, query, start, end, include_content=False):
    window(start, end)
    result, _, _ = client.request("POST", f"{GRAPH}/v1.0/security/runHuntingQuery",
                                  {"Query": query, "Timespan": f"{start}/{end}"}, retry=True)
    if not isinstance(result.get("results"), list) or not isinstance(result.get("schema"), list):
        raise ValueError("Expected hunting schema and results")
    if len(result["results"]) >= 100000:
        raise RuntimeError("Possible hunting truncation at 100,000 rows; narrow time range")
    store.save(digest(["hunting", query, start, end]), [
        normalize("defender-hunting", r, digest(query), include_content)
        for r in result["results"]
    ])


def transcripts(client, store, environment, start, end, include_content=False):
    window(start, end)
    parsed = urllib.parse.urlsplit(environment)
    if parsed.scheme != "https" or parsed.path not in ("", "/") or parsed.query:
        raise ValueError("Use the approved Dataverse environment HTTPS origin, without a path")
    columns = "conversationtranscriptid,createdon,modifiedon,conversationstarttime,schematype"
    if include_content:
        columns += ",content,metadata"
    url = query_url(environment.rstrip("/") + "/api/data/v9.2/conversationtranscripts", {
        "$select": columns,
        "$filter": f"modifiedon ge {start} and modifiedon lt {end} and schematype eq 'powervirtualagents'",
    })
    pages(client, store, url, "copilot-studio-transcripts", environment, include_content)
