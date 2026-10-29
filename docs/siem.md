# Export to Sentinel and third-party SIEMs

Export never creates missing source content. Keep **source permission** separate
from **sink write permission**, and metadata separate from restricted content.
Use [the schema](../config/dcr.json), [permissions](permissions.md) and
[data-handling controls](../SECURITY.md).

## Prefer supported native routes

| Source | Sentinel path | Other SIEM / archive path | Caveat / evidence |
|---|---|---|---|
| Entra sign-in/audit/Graph request activity | Entra ID connector/diagnostic settings -> native tables | Diagnostic settings -> Event Hubs or Storage -> vendor consumer | Select categories separately; P1/P2 for sign-ins/Graph logs; Workload ID Premium for service principal risk categories [E7,E10] |
| Defender XDR | Supported Defender XDR connector; configure raw event tables explicitly | Defender streaming API -> Event Hubs/Storage for supported event types | Alerts/incidents and advanced-hunting raw streams are different; not every table or Purview report is a stream [X2] |
| M365/Purview audit | Installed Microsoft 365 solution/connector for explicitly supported workloads/record types | Management Activity API polling -> approved SIEM integration | Do not assume the standard Exchange/SharePoint/Teams connector ingests every Copilot/custom-app record [A5,X3] |
| CopilotActivity | Only a connector whose current documentation lists CopilotActivity | Query/export what is actually ingested using approved destination capabilities | Native table cannot be written with this Logs Ingestion API; don't fabricate its connector [K4,X3] |
| Custom collected records | This repository's DCR/DCE Logs Ingestion API -> AgentActivity_CL | Generic HTTPS JSON, Splunk HEC, or a separately deployed Event Hub forwarder | Custom schema and explicit content safeguards; at-least-once [X1,X4] |
| Instrumented agent traces | Application Insights / Azure Monitor or configured OTLP destination | Supported OTLP collector/backend; vendor exporter | Trace backend != Purview compliance ingestion [S1,S4] |

### Native Entra setup [E7,E10]

1. Prepare the destination and network policy; identify the configuration
   operator separately from the reader (Security Administrator for the
   documented diagnostic setup; Sentinel Contributor on workspace).
2. In Entra **Monitoring & health > Diagnostic settings**, create a named pilot
   setting. Select audit, interactive/noninteractive user, service principal
   and managed identity categories needed by your agent access patterns.
   Add **MicrosoftGraphActivityLogs** for Graph HTTP request visibility.
3. Choose Log Analytics, Storage or Event Hubs. For Sentinel use its linked
   workspace/Entra connector as documented. For external SIEM choose its
   vendor-supported Event Hubs consumer, separate consumer group and checkpoint
   storage; preserve event IDs and partition offsets.
4. Generate a synthetic read as a pilot identity; inspect native tables.
   Microsoft Graph logs commonly arrive within 30 minutes, occasionally up
   to two hours. They expose request URIs and response sizes, not bodies.
5. Test consumer restart, checkpoint recovery, backlog alarms and duplicate
   handling. Verify destination retention and costs before broad rollout.
6. Roll back by disabling only the named diagnostic setting/consumer after
   recording the last successful offset; preserve required investigation data.

Event Hub authorization is independent of Graph OAuth. Use the consumer's
documented least-privilege receive identity (for Entra-supported consumers,
Azure Event Hubs Data Receiver) and storage checkpoint access; do not hand
source Graph tokens to a SIEM.

### Native Defender streaming [X2]

Open the Defender portal's streaming API settings with an authorized security
administrator, configure the approved Event Hub/Storage destination, select
**only supported event types**, and follow the current Defender prerequisites.
Verify the selected schemas and a synthetic event end to end. Not all hunting
tables are streamable. This reference supplies hunting queries/read collectors,
not an automated live streaming configuration or a guarantee of Copilot content.

## Custom Sentinel route: exact schema, separate write identity [X1,N1]

1. Review the [table request body](../config/table.json). Choose workspace
   region, table plan and approved retention (30 days is an example).
   Create `AgentActivity_CL` using Azure Monitor's table creation UI or
   documented Tables management API. The file is a request body, **not an
   ARM deployment template**.
2. Review [DCR request body](../config/dcr.json). Replace the region/workspace
   resource ID. Table and DCR must be in the documented matching region.
   Create a **Direct** DCR; capture its **immutable** ID and logsIngestion
   endpoint. With private link, configure a DCE and the required network path.
   The DCR resource ID/name is not its immutable ID.
3. Grant the dedicated writer **Monitoring Metrics Publisher on that DCR**.
   It needs no Microsoft Graph consent. Don't grant workspace Contributor
   just to ingest records.
4. Collect the synthetic fixture and send it with a Monitor-scoped credential:

```powershell
python -m agent_audit.cli --db .local\demo.sqlite fixture
$ingestionUrl = "https://YOUR_INGESTION_HOST/dataCollectionRules/dcr-YOUR_IMMUTABLE_ID/streams/Custom-AgentActivity?api-version=2023-01-01"
python -m agent_audit.cli --db .local\demo.sqlite --auth cli send --mode sentinel --host YOUR_INGESTION_HOST --url $ingestionUrl
```

5. Inspect DCR ingestion errors and `AgentActivity_CL | take 5`; confirm
   `Source`, `RecordId`, `TimeGenerated`, and dynamic `Data` match.
6. Rerun send: acknowledged unchanged records are not sent again by this
   outbox. Test failure/restart; a lost acknowledgement can still duplicate.
   Consumers should `summarize arg_max(TimeGenerated, *) by RecordId`.
7. Roll back by stopping the writer and revoking its DCR assignment. Do not
   delete required records to undo ingestion. Keep source collection running
   to its protected spool if approved.

The transport supports only approved HTTPS port 443, TLS verification and JSON.
One event per request is deliberate for reviewable per-event acknowledgement;
this is not a high-throughput production pipeline. Events above 900,000 bytes
fail without truncation. Quarantine/handle oversized events through an approved
secured alternative, not a silent drop. Current service limits are authoritative.

## Generic third-party HTTPS route

The generic receiver contract is **repository-defined**, not an industry
standard: accept one normalized JSON object, validate schema/authentication,
durably store/deduplicate `RecordId`, accept `Idempotency-Key`, and return
204 (or a synchronous JSON 2xx response) only after durable acceptance. 202
requires an additional receipt protocol and is intentionally not acknowledged.

```powershell
# ACCESS_TOKEN here is a destination token, never the source Graph/Management token.
python -m agent_audit.cli --db .local\demo.sqlite send --mode generic --host siem.example.invalid --url https://siem.example.invalid/agent-events
```

`example.invalid` intentionally does not resolve; replace with a verified
receiver implementing that contract. Authenticate and authorize before accepting
payloads, validate size/types, scrub logs, and maintain tenant isolation. No
receiver is deployed by this repository.

## Splunk HEC variant [X4]

Create a restricted HEC token/index using Splunk administration, front HEC with
approved TLS on **443** (the example refuses the common direct 8088 port), and
use `/services/collector/event/1.0`. The sender wraps each normalized record as
`{"sourcetype":"_json","event":{...}}`, uses `Authorization: Splunk <token>`,
and requires JSON `code: 0`.

```powershell
python -m agent_audit.cli --db .local\demo.sqlite send --mode splunk --host splunk.example.invalid --url https://splunk.example.invalid/services/collector/event/1.0
```

HEC success is not a guarantee of searchable/indexed delivery. Indexer
acknowledgement/channel polling is **not implemented**. Use a vendor-supported
forwarder/SDK and receipt handling for production delivery guarantees. Dedup
with `event.RecordId`/extracted `RecordId` in the downstream pipeline; preserve
source event time separately if HEC `_time` defaults to receipt time.

The official vendor documentation URLs were identified but returned 403 during
automated retrieval; wire details were checked against Splunk-owned upstream
Java logging implementation, not generated search text. See [sources](sources.md).

## Operating/reconciliation checklist

Track source window completion, page/blob count, oldest unacknowledged event,
destination rejection, duplicate count and sampled field completeness.
Do not treat HTTP success as semantic ingestion success for every vendor.
Maintain a restricted dead-letter process, retry budget, replay authority,
and documented backlog/retention SLA. Native/custom routing of the same
source can double count or double bill: choose a system of record.

Metadata-only and full-raw representations have independent RecordIds/delivery
receipts; toggling content mode won't silently overwrite an acknowledged
payload. Prefer separate protected databases/destinations for the two modes
and don't count both projections as distinct underlying business interactions.
`Data.NativeId` preserves the source identifier; source-specific namespace and
snapshot version still matter when correlating.
