# Evidence catalog and provenance

Research baseline: **2026-10-28**, with final package/schema checks completed
2026-10-29 UTC. URLs below were retrieved using Microsoft Learn/Azure
documentation tools, official pages, Microsoft-owned upstream repositories,
package registries and vendor-owned source. Search-generated summaries were
discovery aids, **not evidence**. Context7 supplied current Agent Framework
API examples which were checked against installed package signatures.

Source tags in each example/runbook map here. **v1** means the documented
Graph v1.0 contract; **beta** is a preview API unsuitable for production
dependency without accepting change risk. A versioned package, v1 endpoint
or unmarked overview does not prove every feature/location is GA.
Licensing/rollout can change: recheck the linked feature guidance before
customer deployment. No tenant integration was used as source verification.

## Audit and interaction retrieval

| ID | Verified source | Evidence / maturity |
|---|---|---|
| A1 | [Create Audit Search query](https://learn.microsoft.com/en-us/graph/api/security-auditcoreroot-post-auditlogqueries?view=graph-rest-1.0), [get query](https://learn.microsoft.com/en-us/graph/api/security-auditlogquery-get?view=graph-rest-1.0), [list records](https://learn.microsoft.com/en-us/graph/api/security-auditlogquery-list-records?view=graph-rest-1.0) | Saved asynchronous search/status/records, workload-specific permissions; Graph v1 |
| A2 | [Audit Copilot activities](https://learn.microsoft.com/en-us/purview/audit-copilot) | CopilotInteraction metadata/resource references; workload-specific auditing, not universal text export |
| A3 | [getAllEnterpriseInteractions](https://learn.microsoft.com/en-us/graph/api/aiinteractionhistory-getallenterpriseinteractions?view=graph-rest-1.0) | Graph v1 application AiEnterpriseInteraction.Read.All, licensed users, filter/paging, excludes Studio-created agents |
| A4 | [Audit overview](https://learn.microsoft.com/en-us/purview/audit-solutions-overview), [retention](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies), [enable audit](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable) | Standard/Premium, 180-day baseline and eligible one-year workloads; enablement/retention roles, not a universal SLA |
| A5 | [Management Activity API reference](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference) | v1.0 feed subscriptions, scopes, 24-hour/7-day listing constraints, NextPageUri and contentUri, duplicate/late content |

## Identity, security and Copilot Studio

| ID | Verified source | Evidence / maturity |
|---|---|---|
| C1 | [Work with Copilot Studio transcripts](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-transcripts-powerapps) | Dataverse role/environment/retention/redaction limits; native feature |
| C2 | [ConversationTranscript entity](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/conversationtranscript?view=dataverse-latest) | Exact entity set/columns, content/metadata are strings; Dataverse v9.2 |
| C3 | [Dataverse OAuth](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth) | Environment audience, delegated user_impersonation and application-user security roles |
| D1 | [List alerts_v2](https://learn.microsoft.com/en-us/graph/api/security-list-alerts_v2?view=graph-rest-1.0) | SecurityAlert.Read.All / product RBAC; Graph v1 |
| D2 | [List incidents](https://learn.microsoft.com/en-us/graph/api/security-list-incidents?view=graph-rest-1.0) | SecurityIncident.Read.All; Graph v1 |
| D3 | [runHuntingQuery](https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery?view=graph-rest-1.0) | ThreatHunting.Read.All, Query/Timespan, schema/results, row/resource limits; Graph v1, not older Defender audience |
| E1 | [List signIns](https://learn.microsoft.com/en-us/graph/api/signin-list?view=graph-rest-1.0) | AuditLog.Read.All, supported user roles and CA-details permission; v1 limitations |
| E2 | [List directoryAudits](https://learn.microsoft.com/en-us/graph/api/directoryaudit-list?view=graph-rest-1.0) | AuditLog.Read.All, delegated roles/filter; Graph v1 |
| E3 | [List servicePrincipals](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list?view=graph-rest-1.0) | Application.Read.All, ordinary directory inventory; Graph v1 |
| E4 | [Risky agents](https://learn.microsoft.com/en-us/entra/id-protection/concept-risky-agents) | Native offline identity-risk detections, learning/report retention, OBO attribution; verify tenant feature licensing |
| E5 | [List riskyAgents](https://learn.microsoft.com/en-us/graph/api/riskyagent-list?view=graph-rest-beta) | IdentityRiskyAgent.Read.All; **beta** snapshot |
| E6 | [List agentIdentity](https://learn.microsoft.com/en-us/graph/api/agentidentity-list?view=graph-rest-beta) | AgentIdentity.Read.All, owner/Agent ID Administrator behavior; **beta** inventory |
| E7 | [Entra -> Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/connect-azure-active-directory) | Diagnostic categories, sign-in streaming licensing, service-principal-risk Workload ID Premium requirement |
| E8 | [Entra retention](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-reports-data-retention) | 7-day Free / 30-day P1/P2 audit/sign-ins; Graph logs need destination |
| E9 | [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) | Token subject, Agents/Agent Users targeting, licensing, exclusions and feature-specific preview limits |
| E10 | [Microsoft Graph activity logs](https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview) | P1/P2, Security Administrator, diagnostic export to workspace/Event Hubs/Storage; request metadata and latency, no bodies |
| E11 | [Target agent identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-target-agent-identities), [autonomous-agent policies](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-autonomous-agents) | Agents/Agent Users preview selections, blueprint/attribute targeting, Report-only high-risk block; risk-based CA requires additional P2/E5 pairing or E7; not ordinary user-group assignment |
| E12 | [Create/manage Entra groups](https://learn.microsoft.com/en-us/entra/fundamentals/how-to-manage-groups), [manage agent identities](https://learn.microsoft.com/en-us/entra/agent-id/manage-agent-identities-admin) | Assigned security-group creation/owners and identity-object inventory; group membership is distinct from agent CA targeting |
| E13 | [Add group members](https://learn.microsoft.com/en-us/graph/api/group-post-members?view=graph-rest-1.0) | Service principals supported in security groups, not M365 groups; service-principal addition requires GroupMember.ReadWrite.All plus Application.ReadWrite.All and applicable caller role |

## Query schemas (native, not repository inventions)

| ID | Verified source | Evidence / maturity |
|---|---|---|
| K1 | [CloudAppEvents](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table) | Native Defender columns and RawEventData; Defender for Cloud Apps M365 activity prerequisites |
| K2 | [Copilot audit schema](https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema) | CopilotEventData, accessed resources, labels and emitted interaction fields |
| K3 | [AlertEvidence](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertevidence-table), [AlertInfo](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-alertinfo-table) | AlertId join, OAuthApplicationId/AccountObjectId; evidence availability follows deployed products |
| K4 | [CopilotActivity](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/copilotactivity) | Native table columns, AgentId meaning; **Ingestion API not supported** |
| K5 | [OfficeActivity](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/officeactivity) | Native M365 audit schema; ingestion API not supported, connector coverage matters |
| K6 | [AADServicePrincipalSignInLogs](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs) | Native app sign-in columns; not the same schema as Graph signIns |
| K7 | [AppDependencies](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/appdependencies) | Workspace-based Application Insights dependency columns / Properties |
| K8 | [MicrosoftGraphActivityLogs](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/microsoftgraphactivitylogs) | HTTP request/status/resource/identity fields; ingestion API not supported |
| N1 | [Table](../config/table.json), [DCR](../config/dcr.json), [normalizer](../agent_audit/store.py) | **Repository-defined** AgentActivity_CL schema; not native product columns |

## Purview runtime and policies

| ID | Verified source | Evidence / maturity |
|---|---|---|
| P1 | [Compute protection scopes](https://learn.microsoft.com/en-us/graph/api/userprotectionscopecontainer-compute?view=graph-rest-1.0) | ProtectionScopes.Compute.User/All, ETag and scope modes; Graph v1 |
| P2 | [processContent](https://learn.microsoft.com/en-us/graph/api/userdatasecurityandgovernance-processcontent?view=graph-rest-1.0), [response](https://learn.microsoft.com/en-us/graph/api/resources/processcontentresponse?view=graph-rest-1.0) | Content.Process.User/All, policy actions/errors/state; Graph v1 submission/evaluation, not extraction |
| P3 | [Create contentActivity](https://learn.microsoft.com/en-us/graph/api/activitiescontainer-post-contentactivities?view=graph-rest-1.0) | ContentActivity.Write; Graph v1 activity submission |
| P4 | [Use the Purview API](https://learn.microsoft.com/en-us/purview/developer/use-the-api) | Register app, compute/process, online/offline and in-app action responsibilities |
| P5 | [Entra-registered AI apps](https://learn.microsoft.com/en-us/purview/ai-entra-registered) | PAYG, collection, SIT prompt blocking, roles, IRM/CC/eDiscovery/retention; individual solution/preview prerequisites apply |
| P6 | [Test integrated application](https://learn.microsoft.com/en-us/purview/developer/how-to-test-an-ai-application-integrated-with-purview-sdk) | Synthetic test sequence, connectedAIAppInteraction, audit/activity/policy validation |
| P7 | [New-DlpComplianceRule](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancerule?view=exchange-ps), [Purview permissions](https://learn.microsoft.com/en-us/purview/purview-permissions) | Cmdlet Example 4 app location/UploadText restrictAccess, separate solution role groups; manual administration |
| P8 | [Microsoft 365 Copilot DLP location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about) | Custom-template location, user/group scope, separate SIT/label rules, simulation, four-hour propagation, upload limitations; prompt/external-email blocking preview and admin-unit rollout |
| P9 | [CC setup](https://learn.microsoft.com/en-us/purview/communication-compliance-configure), [CC policies](https://learn.microsoft.com/en-us/purview/communication-compliance-policies) | Copilot interactions template/classifiers, audit/roles, supported mail-enabled scoped-user groups, individual mailbox reviewers; non-M365 AI PAYG prerequisites |
| P10 | [IRM setup](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure), [templates](https://learn.microsoft.com/en-us/purview/insider-risk-management-policy-templates), [policy management](https://learn.microsoft.com/en-us/purview/insider-risk-management-policies) | Risky AI usage human scope, browser/indicator/trigger prerequisites, scoring/threshold workflow; distinct from agent-specific monitoring |
| P11 | [Monitoring agents in IRM](https://learn.microsoft.com/en-us/purview/insider-risk-management-monitoring-agents) | Default Risky Agents **preview** policy, Studio/Foundry/P4AI SDK agents, guest-content limitations and no administrative-unit agent-alert support; no claimed CA risk-score equivalence |
| P12 | [Create/manage Exchange distribution lists](https://learn.microsoft.com/en-us/exchange/recipients-in-exchange-online/manage-distribution-groups/manage-distribution-groups) | EAC Recipients > Groups > Distribution list creation, recipient permissions and controlled membership for CC scope |

## SDKs, CLI and telemetry

| ID | Verified source | Evidence / maturity |
|---|---|---|
| S1 | [Microsoft OpenTelemetry for Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/microsoft-opentelemetry), [upstream](https://github.com/microsoft/opentelemetry-distro-python) | New distro/manual scopes/exporters; former Agent 365 observability packages deprecated for new integrations |
| S2 | [Observability authentication](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability-authentication-setup) | Four auth scenarios, resource/permissions, delegated vs S2S routes, baggage and token resolver |
| S3 | [Framework observability examples](https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/observability/README.md) | OpenTelemetry, sensitive telemetry opt-in, framework/client spans; package-specific APIs locally verified |
| S4 | [Framework OpenAI package](https://github.com/microsoft/agent-framework/blob/main/python/packages/openai/README.md), [Azure Monitor Python](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python) | OpenAIChatClient current construction and Azure Monitor configuration, distinct destination |
| S5 | [Agent 365 SDK](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-sdk), [Python upstream](https://github.com/microsoft/Agent365-python) | Extends existing hosted agents, runtime/tooling/notifications, agent-user/mailbox Frontier limits |
| S6 | [CLI overview](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/agent-365-cli), [command reference](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/reference/cli/), [upstream](https://github.com/microsoft/Agent365-devTools), [NuGet 2.0.1](https://www.nuget.org/packages/Microsoft.Agents.A365.DevTools.Cli/2.0.1) | .NET 8+, setup/query/admin roles; 2.0.1 published 2026-10-20, restored locally; tenant setup not run |
| F1 | [Foundry framework tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-framework) | Tracing GA for prompt/hosted agents; workflow/external agents preview; instrumentation/content/project prerequisites |

Exact resolved Python versions are [locked](../requirements-sdk.lock).
Registry metadata checked: [Framework core](https://pypi.org/project/agent-framework-core/1.22.0/),
[Framework OpenAI](https://pypi.org/project/agent-framework-openai/1.17.0/),
[Microsoft distro](https://pypi.org/project/microsoft-opentelemetry/1.5.0/),
[Azure Monitor](https://pypi.org/project/azure-monitor-opentelemetry/1.8.11/),
[Azure Identity](https://pypi.org/project/azure-identity/1.27.0/).
Installed SDK imports, constructor shape and offline spans were checked, not
just copied from a moving main branch.

## SIEM transport and build identity

| ID | Verified source | Evidence / maturity |
|---|---|---|
| X1 | [Logs Ingestion API/REST shape](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview#rest-api-call), [PowerShell REST example](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-code?tabs=powershell) | Custom table, Direct DCR/DCE, same region, Monitoring Metrics Publisher, upload contract |
| X2 | [Defender streaming API](https://learn.microsoft.com/en-us/defender-xdr/streaming-api) | Supported hunting streams -> Event Hubs/Storage; prerelease notice and product-specific limits |
| X3 | [Sentinel connector catalog](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference#microsoft-office-365) | Current connector-specific workloads/table prerequisites; catalog has preview notice, don't infer universal Copilot ingestion |
| X4 | [Splunk-owned HEC sender](https://github.com/splunk/splunk-library-javalogging/blob/main/src/main/java/com/splunk/logging/HttpEventCollectorSender.java), [error handling](https://github.com/splunk/splunk-library-javalogging/blob/main/src/main/java/com/splunk/logging/HttpEventCollectorErrorHandler.java) | Authorization Splunk, event/1.0 route, JSON errors. HEC JSON event wrapper checked against vendor implementation; no vendor source copied |
| X5 | [GitHub OIDC -> Azure](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect), [Azure DevOps federation](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops) | Federated service connection/subject, no stored client secret; approval/RBAC still required |

## User repository prior art (private, read-only)

The user authorized reviewing these repositories; they are **not product
support evidence**. No scripts/builds/installers were run there and no private
code, tenant IDs, credentials or customer content was republished.

| Repository under mward-msft1 | What informed this original implementation |
|---|---|
| AI_Agent_Graph_API; aiinteractions_query; Agent_Framework; Workday_and_Purview_APIIntergration | Available READMEs were essentially titles; no reusable verified implementation evidence |
| Test_GCP_Agent_A365_Purview | Read-only README: explicit tenant/auth pinning, Purview submission vs downstream enforcement, dry run != no read; translated into original safeguards |
| Copilot-Studio-Prompt-and-Response | Read-only README makes broad coverage claims; those claims were not adopted without Microsoft evidence |
| Agent_Examples_A365; Sample_Amazon_Agent_with_SDK; MCP_drift | Available READMEs were title-only; not used as functional proof |
| risky_agent_test | Read-only context reinforced tool discovery != tool execution, identity provenance and synthetic tests; private deployment values deliberately excluded |

Other supplied candidate paths were not exhaustively audited. This is a
bounded relevant-source review, not a claim every repository/file was searched.
Examples in this repository were written originally; upstream code is linked
for API evidence rather than copied. Honor upstream licenses when extending.

## Access failures and unavailable evidence

Before interactive mode, local directory discovery, `gh repo view`, Python
version and Azure documentation discovery were denied by the tool approval
layer with:
**"Permission denied because no interactive user response was available"**.
That is an **approval failure**, not proof of missing local directories or
GitHub network/token authorization failure. The user explicitly enabled
interactive mode and requested retries through normal approvals; these
operations subsequently succeeded. No inaccessible approval prompt remains.

Other retrieval failures were transport/product-path issues, not permissions
bypass attempts: NuGet version-API/public PyPI file TLS handshakes failed;
TLS verification was never disabled. The pinned CLI restored normally via
NuGet afterward. `Agent365-devTools/releases/latest` returned 404 (no latest
release); NuGet supplied the verified version. Some guessed documentation
paths returned 404 and are not cited as evidence. Splunk help pages returned
403; only publicly accessible vendor-owned source was used for wire details.
No denied local/private source was retrieved via an alternate access method.
