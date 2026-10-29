# Coverage and honest limitations

Baseline retrieved 2026-10-28. Bracketed source IDs resolve in
[sources](sources.md). "Available" means the documented surface can return the
data under its prerequisites, not that every tenant/agent emits it.

## Product and signal matrix

| Agent / source | Prompts and responses | Data/resource access and tool calls | Violations and risky behavior | Dependencies and gaps |
|---|---|---|---|---|
| Microsoft 365 Copilot audit [A1,A2,K2] | Message IDs/metadata; **not a text-content export** | `CopilotEventData.AccessedResources` and labels when emitted; plugin metadata is not a full invocation trace | Separate DLP/product detections; usage alone is not a breach | Audit-enabled/licensed workloads; connector routes and schema vary |
| M365 Copilot interaction export [A3] | `body`, cards/attachments as returned, userPrompt/aiResponse | Returned contexts/links are not a full record of every downstream service call | No universal inline policy verdict field | `AiEnterpriseInteraction.Read.All` **application only**; licensed users with Microsoft Copilot with Graph-grounded chat service plan; no delta; **excludes Copilot Studio-created agents** |
| Copilot Studio [C1,C2] | Recorded transcripts in Dataverse where supported; **SharePoint-grounded answers can be REDACTED**, while question/source content may remain | Transcript events/node data and optional App Insights instrumentation; not all connector downstream actions guaranteed | Power Platform data policies, Purview and Defender each cover their documented scope | Bot Transcript Viewer; no Dataverse for Teams transcript writes; developer-environment and admin recording restrictions; storage and Dataverse retention differ |
| Microsoft Foundry / Agent Framework [S3,S4,F1] | Explicit sensitive telemetry opt-in; tool/content paths depend on instrumentation | Client/service traces and instrumented tool spans; private tool data must be minimized | Content-safety/Prompt Shields or Defender findings only if configured and emitted; trace errors are not such findings | Project/model permissions, exporter and supported instrumentation; do not assume hosted service telemetry or Purview collection from client traces alone |
| Custom third-party agents on AWS/GCP/on-prem [S1,S2,S5,P1-P5] | Manual instrumentation or supported auto-instrumentation; Purview API submission for an Entra-known user; no retroactive capture | Instrument each model and tool boundary, record approved resource references; backend/cloud audit is separate | Purview returned policy actions can be enforced in app; identity risk requires supported identity; network controls cover only observed traffic | Hosting is not the barrier; missing instrumentation, no known user, unsupported auth flow, disabled collection or inaccessible runtime are |
| Agent 365 registered / registry-synced agents [S5] | **Registration alone does not capture content** | Inventory != runtime spans; native platform integrations differ | Agent identity/Defender/Purview integrations depend on configuration | Agent user/mailbox and notifications require Frontier preview per SDK docs; no claim all inventory paths offer same SDK capability |
| Entra sign-in/directory audit [E1,E2,E3,E7] | None | Token issuance, application/resource context, directory changes; Graph request activity when configured | Native identity-risk signals separately; failures/volume are investigative leads | P1/P2 for sign-in streaming; diagnostic categories separate user/noninteractive/service principal/managed identity; Graph v1 signIns collector is not an exhaustive workload sign-in export |
| Entra ID Protection agents [E4,E5] | None | Suspicious identity/resource access detections, not file bodies/tool payloads | Native risky agent state; offline detections and learning mode; OBO activity risk is attributed to user | Agent ID prerequisites and evolving Agent 365 licensing; implemented riskyAgents endpoint is **beta** and explicitly gated |
| Defender XDR alerts/incidents/hunting [D1-D3,K1,K3] | Do not assume prompt text in security alerts | Only connected products/tables and emitted evidence | Real product detections, not every Purview report or all AI activity | Licensed deployed products, connector settings, hunting/RBAC limits; no universal "all AI events" query |
| Purview runtime APIs [P1-P5] | App submits selected input/output for evaluation/collection; this family does **not extract stored interactions** | Metadata the app actually supplies; Purview doesn't independently fetch a resource URL | Inline actions must be enforced; offline submission is not blocking | Entra-registered app, known user context, policy application ID, permissions, pay-as-you-go and collection policies; unattended no-user scenarios need separate verified design |
| M365 Copilot DLP / CC [P8,P9] | Supported prompt/grounding evaluation and authorized CC review; different collection and access paths | Native Copilot locations only; DLP doesn't scan directly uploaded prompt files | DLP can enforce supported restrictions; CC matches need review, not inline blocking | Human prompt/user scope, SIT-prompt blocking preview, supported CC mail-enabled groups and individual reviewers; see [M365 recipes](m365-policy-recipes.md) |
| Purview IRM [P10,P11] | Available content depends on supported connections and reviewer access; guest agent interactions have content limits | User Risky AI usage and default Risky Agents preview are separate | Agent activity/content risk is not Entra identity risk; no automatic CA block asserted | Risky Agents supports Studio/Foundry/P4AI SDK agents per current docs; no administrative-unit agent-alert support or claimed arbitrary agent-group scope |

First-party extensions can appear through multiple surfaces. A publisher label
does not determine coverage: confirm the **experience, host, user license,
identity flow, connector, instrumentation and policy location** for each pilot.
No collector can reconstruct content that was never logged or was redacted.

## Availability, retention and latency

| Surface | Retention / latency / bounds | Maturity baseline |
|---|---|---|
| Purview Audit | Audit Standard commonly 180 days; Premium/eligible workloads and custom retention differ. Verify actual license/retention policy [A4]. Ingestion is asynchronous and workload-dependent; query completion is also asynchronous | v1.0 Audit Search API; per-tenant daily and concurrent submission quotas |
| Management Activity API | Subscription required before content availability. Listing uses <=24h windows with start no older than 7 days; content availability time is not the event time. Late/duplicate/out-of-order records possible [A5] | Published v1.0 feed; not historical archive or full conversation store |
| Copilot export | No delta; availability varies by licensed experience. No blanket retention/latency SLA asserted. Verify retention with compliance owner; query overlapping bounded date ranges [A3] | v1.0 documented; beta alternatives not needed here |
| Copilot Studio | Dataverse bulk deletion commonly 30 days; Studio storage up to 28 days; transcript saved after 30 minutes inactivity, larger records split at 1 MB [C1]. Admin settings can disable recording | Documented service feature; environment/channel restrictions apply |
| Entra | Default audit/sign-in retention generally 7 days Free / 30 days P1/P2 [E8]; diagnostic export extends retention at destination. Agent risk detections report up to 90 days [E4] | Graph agent inventory/risky-agent examples here use beta; not production-supported beta contracts |
| Defender hunting | Default/raw retention commonly 30 days; API and licensing limits apply. Use smaller windows and bounded result counts [D3] | Graph v1.0 hunting endpoint; underlying table maturity varies |
| Instrumented OTel | Queue/export delay, sampling, dropped spans, failures and backend TTL all affect completeness. Default sampling is not a compliance delivery guarantee | Pinned released packages; some dependencies/GenAI semantics remain beta |
| Purview custom-app reports | Official guidance says allow at least a day for reports; some test views may appear sooner [P5,P6]. Don't promise immediate DLP-to-SIEM availability | Runtime endpoints documented v1.0; individual Purview solution features/locations can be preview |
| Sentinel/custom SIEM | Connector, queue, DCR transform and index latency; retention and cost depend on table plan/configuration | Custom table is repository-defined; never describe it as a native Microsoft schema |

## Gaps and planned customer decisions

No background SaaS content scraping, encrypted/password-protected data recovery,
cross-tenant or arbitrary cloud enumeration, eDiscovery export automation, or
Defender alert creation is implemented. No claim that all Purview DSPM/IRM/CC
analytics have an equivalent public export API. The portal and approved
eDiscovery process remain necessary for some investigations.

Before live deployment choose the agent inventory/user scope, required signal
set, lawful content-retention basis, allowed destinations, licenses/billing,
pilot identities and production owner. Set a service-specific latency budget,
reconciliation interval and failure alert. Keep a measured coverage ledger:
synthetic scenario -> expected source -> observed record ID/time -> missing
field -> documented reason. An empty collection is not proof of no activity.
