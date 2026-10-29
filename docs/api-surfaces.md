# API families and real HTTP shapes

This distinction prevents the common mistake of treating "Microsoft security
graph" as a universal conversation API. The runnable implementations live in
[collect.py](../agent_audit/collect.py) and [purview.py](../agent_audit/purview.py).
All examples use commercial-cloud endpoints and documented API versions.

| Family | Actual surface | Use / source |
|---|---|---|
| Graph **security** | `/v1.0/security/alerts_v2`, `/incidents`, `/runHuntingQuery` | Defender detections and connected hunting data [D1-D3] |
| Graph **security Audit Search** | `/v1.0/security/auditLog/queries` | Saved asynchronous Purview audit searches [A1] |
| Graph **Copilot** | `/v1.0/copilot/users/{id}/interactionHistory/getAllEnterpriseInteractions` | Licensed Copilot interaction export; NOT a `/security` API [A3] |
| Graph **auditLogs/directory** | `/v1.0/auditLogs/signIns`, `/directoryAudits`, `/servicePrincipals` | Identity activity and ordinary app inventory [E1-E3] |
| Graph **Agent ID / ID Protection** | `/beta/servicePrincipals/microsoft.graph.agentIdentity`, `/beta/identityProtection/riskyAgents` | Preview inventory/current risk state [E5,E6] |
| Purview **runtime data security in Graph** | `/v1.0/users/{id}/dataSecurityAndGovernance/...` | Compute applicable policy, submit/evaluate content; not an analytics export [P1-P4] |
| Office 365 Management Activity | `https://manage.office.com/api/v1.0/{tenant}/activity/feed/...` | Subscribed audit content blobs [A5] |
| Dataverse Web API | `https://{org}/api/data/v9.2/conversationtranscripts` | Supported Copilot Studio transcripts [C1,C2] |
| Azure Monitor Logs Ingestion | DCR/DCE endpoint `/dataCollectionRules/{immutableId}/streams/{stream}` | Destination write, not source retrieval [X1] |

The similarly named Purview Data Map/Unified Catalog APIs govern data assets;
they are **not** Microsoft 365 compliance audit or prompt-capture APIs.

## Purview audit: create, poll, retrieve [A1]

```http
POST https://graph.microsoft.com/v1.0/security/auditLog/queries
Authorization: Bearer <GRAPH_TOKEN>
Content-Type: application/json

{
  "displayName": "Synthetic pilot audit search",
  "filterStartDateTime": "2026-10-27T00:00:00Z",
  "filterEndDateTime": "2026-10-28T00:00:00Z",
  "operationFilters": ["CopilotInteraction"]
}
```

```http
GET https://graph.microsoft.com/v1.0/security/auditLog/queries/<RETURNED_ID>
Authorization: Bearer <GRAPH_TOKEN>
```

Only when `status == "succeeded"`:

```http
GET https://graph.microsoft.com/v1.0/security/auditLog/queries/<RETURNED_ID>/records
Authorization: Bearer <GRAPH_TOKEN>
```

Follow `@odata.nextLink` unchanged after checking its trusted origin. Failed,
cancelled, unknown status, or a timeout is not an empty successful result.
Query APIs have service-specific tenant quotas; a 429 can carry Retry-After.

## Licensed interaction export [A3]

```http
GET https://graph.microsoft.com/v1.0/copilot/users/<USER_ID>/interactionHistory/getAllEnterpriseInteractions?$top=100&$filter=createdDateTime%20gt%202026-10-27T00:00:00Z%20and%20createdDateTime%20lt%202026-10-28T00:00:00Z
Authorization: Bearer <APPLICATION_GRAPH_TOKEN>
```

Synthetic response fragment (not a guarantee all properties always appear):

```json
{
  "value": [
    {
      "id": "synthetic-prompt-001",
      "sessionId": "synthetic-thread",
      "requestId": "synthetic-turn",
      "createdDateTime": "2026-10-27T12:00:00Z",
      "interactionType": "userPrompt",
      "body": {"contentType": "text", "content": "Summarize EXAMPLE-ONLY."},
      "attachments": [],
      "contexts": [],
      "links": []
    }
  ]
}
```

## Hunting [D3]

```http
POST https://graph.microsoft.com/v1.0/security/runHuntingQuery
Authorization: Bearer <GRAPH_TOKEN>
Content-Type: application/json

{
  "Query": "CloudAppEvents | where ActionType == \"CopilotInteraction\" | take 10",
  "Timespan": "2026-10-27T00:00:00Z/2026-10-28T00:00:00Z"
}
```

Graph uses **ThreatHunting.Read.All**. The older Defender endpoint
`api.security.microsoft.com/api/advancedhunting/run` has a different audience
and permission model; do not copy `AdvancedHunting.Read.All` into the Graph
permission registration.

## Management Activity API [A5]

```http
GET https://manage.office.com/api/v1.0/<TENANT>/activity/feed/subscriptions/content?contentType=Audit.General&startTime=2026-10-27T00:00:00Z&endTime=2026-10-28T00:00:00Z
Authorization: Bearer <MANAGEMENT_TOKEN>
```

Follow `NextPageUri` response **header**, then retrieve each trusted `contentUri`
descriptor. Those content blobs contain arrays of audit records, not OData
`value` objects. Audit record schemas differ by workload.

## Purview content: three different write/evaluation operations [P1-P4]

1. `POST .../protectionScopes/compute` with activities and the **policy
   application location ID**.
2. `POST .../processContent` with `contentToProcess`, activity metadata and
   `processConversationMetadata` text content when evaluation is required.
   Send the cached ETag as `If-None-Match`.
3. If no applicable policy exists, optional
   `POST .../activities/contentActivities` with metadata, not an assumed full
   content archive.

The [synthetic probe](../examples/purview_probe.py) builds the real bodies.
It handles multiple scopes conservatively, refreshes modified policies, blocks
on errors/unknown actions and distinguishes asynchronous observation from an
inline verdict. It is not a source collector, a full SDK middleware integration,
or an automated policy deployment tool.
