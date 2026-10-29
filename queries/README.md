# Query library

| File | Engine / prerequisites | What it establishes |
|---|---|---|
| [Copilot metadata](defender/copilot-metadata.kql) | Defender XDR advanced hunting; Defender for Cloud Apps with M365 activities enabled | Available Copilot audit metadata, not content |
| [Resource labels](defender/copilot-resource-labels.kql) | Same | References to labeled files; not a violation |
| [Agent alerts](defender/agent-alerts.kql) | Defender AlertInfo/AlertEvidence populated by licensed products | Product alerts linked to curated account object IDs |
| [Native Copilot](sentinel/copilot-native.kql) | Sentinel connector explicitly producing CopilotActivity | Native audit records; LLMEventData is workload-specific |
| [Office activity](sentinel/office-activity.kql) | M365 connector and supported Copilot record routing | Alternate layout; confirm installed connector support |
| [Sign-in failures](sentinel/agent-signin-failures.kql) | Entra service principal diagnostics; curated app IDs | Threshold hypothesis, not an ID Protection detection |
| [Sign-in details](sentinel/agent-signin-details.kql) | Same; Agent field available | Agentic sign-in context without speculative JSON paths |
| [Custom risky agents](sentinel/custom-risk.kql) | This repo's custom table + beta risk collection | Reported high-risk state; preview dependency |
| [Content triage](sentinel/custom-content-triage.kql) | Custom table + approved raw interaction export | Keyword candidate; no guarantee of attack detection |
| [Resource volume](sentinel/custom-resource-volume.kql) | Custom metadata ingestion | High resource-reference volume hypothesis |
| [Azure Monitor traces](sentinel/azure-monitor-traces.kql) | Workspace-based Application Insights | Instrumented spans and failures |
| [Graph data access](sentinel/graph-data-access.kql) | Entra P1/P2; Graph activity diagnostic logs | HTTP resource path, status, response size; not bodies or proof of exfiltration |

Sources are tagged in each query and resolved in [the catalog](../docs/sources.md).
These files are **queries**, not enabled analytics rules. Review thresholds against a
benign baseline, entity mapping, cost, permissions and false positives before scheduling.
KQL dialects/schemas differ: Defender files go to `runHuntingQuery`; Sentinel files go
to Log Analytics/Sentinel. A valid KQL shape is not proof the tenant has a table.

Run `TableName | getschema` and a short `take 5` in the intended environment first.
Confirm exact ActionType values against the in-portal schema. Do not union absent
tables with fuzzy resolution and mistake missing telemetry for a clean environment.
Offline checks only check library structure; actual KQL binding requires a tenant.

## Correlation

Use audit `Id` to deduplicate within its feed. Copilot `ThreadId`, message IDs, and
interaction `sessionId`/`requestId` can help correlate *when actually present*; a
thread contains multiple turns. Entra `appId` is a client application ID, `id` of a
service principal is a tenant object ID, and blueprint ID is a different object.
Maintain a curated mapping with tenant, source, ID type and effective dates.
Native CopilotActivity describes AgentId as a version ID: do not join it blindly
to an Entra object ID. `TenantId` in Log Analytics is the workspace ID in several
tables, not necessarily the source Entra tenant.

An OTel trace ID (`OperationId` in Application Insights) is not automatically
propagated into native audit records. Instrument your tool boundary to record a
non-secret request ID and trace ID mapping. User/time proximity joins are
investigative leads, not proof the same agent accessed data. Prompt injection,
policy violations, and exfiltration are different concepts: only a real policy
decision or product detection establishes its corresponding signal.
