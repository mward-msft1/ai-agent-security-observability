# Permissions, audiences, roles and licensing

Grant only the row needed by a collector. OAuth permissions, service RBAC,
product licensing, data availability and network access are **independent
requirements**. Application permissions require tenant admin consent.
For delegated permissions below, plan explicit admin consent as well; do not
rely on end-user consent. Personal Microsoft accounts are not supported.

Microsoft Graph rows use token resource `https://graph.microsoft.com` and
app-only scope `https://graph.microsoft.com/.default`. Delegated scopes and
user roles still apply independently. A Graph access token can't be used for
Management Activity, Azure Monitor, Dataverse, or Agent 365 observability.

## Read/query collectors

| Operation / implementation | Exact OAuth permissions | Delegated / application; service roles | License / availability; source |
|---|---|---|---|
| Create/get/list Audit Search query and records (`audit`) | `AuditLogsQuery.Read.All` for cross-workload Copilot/general search. Workload alternatives: `AuditLogsQuery-Entra.Read.All`, `AuditLogsQuery-CRM.Read.All`, `AuditLogsQuery-Endpoint.Read.All`, `AuditLogsQuery-Exchange.Read.All`, `AuditLogsQuery-OneDrive.Read.All`, `AuditLogsQuery-SharePoint.Read.All` | Both. Match workload scope to desired data; the first permission listed in an API table isn't a universal entitlement to every workload. Portal operators need Audit Reader/Manager (View-Only Audit Logs/Audit Logs); cmdlet roles are in Exchange. Do not assume portal RBAC alone grants API consent | Appropriate Purview Audit subscription; retention and workload entitlement apply [A1,A4] |
| M365 Copilot interactions (`interactions`) | `AiEnterpriseInteraction.Read.All` | **Application only**. Delegated unsupported. Curate licensed user IDs. No extra directory read permission needed when IDs are supplied | Valid M365 Copilot license with Microsoft Copilot with Graph-grounded chat plan; not Copilot Studio [A3] |
| Entra sign-ins (`signins`) | `AuditLog.Read.All` | Both; delegated Reports Reader, Security Reader/Operator/Admin or Global Reader per endpoint. Reading applied CA details additionally needs a documented CA-reading role and `Policy.Read.ConditionalAccess` (or broader supported permission) | Sign-in retention/license prerequisites; P1/P2 for streaming. v1.0 endpoint isn't full workload-sign-in coverage [E1,E7,E8] |
| Directory audit (`directory-audit`) | `AuditLog.Read.All` | Both; delegated Reports Reader or Security Reader/Admin | Directory activity retained by tenant SKU; not prompt content [E2] |
| Ordinary service principals (`service-principals`) | `Application.Read.All` | Both; default directory readers or supported role per endpoint, subject to tenant restrictions. Do not grant write scopes for inventory | Ordinary app inventory, not an AI classification service [E3] |
| Agent identities (`agent-identities`) | `AgentIdentity.Read.All` | Both; nonowner delegated admins use Agent ID Administrator; owner exceptions documented. Beta | Agent ID availability/tenant onboarding [E6] |
| Risky agents (`risky-agents`) | `IdentityRiskyAgent.Read.All` | Both; delegated Security Reader/Operator/Admin or Global Reader. Beta | ID Protection agent feature/licensing; no text content [E4,E5] |
| Defender alerts (`alerts`) | `SecurityAlert.Read.All` | Both; delegated Security Reader/Operator/Admin or Global Reader; product RBAC/data scope still matters | Deployed licensed Defender products [D1] |
| Defender incidents (`incidents`) | `SecurityIncident.Read.All` | Both; same delegated reader-role family | Defender incident sources/correlation, not all AI activity [D2] |
| Graph hunting (`hunting`) | `ThreatHunting.Read.All` | Both; authorized Defender hunting data access and assigned RBAC scope | Tables require their licensed connected products; API time/row/CPU limits [D3,K1] |
| Management feed list/content (`management`) | Office 365 Management APIs **application** `ActivityFeed.Read`; add `ActivityFeed.ReadDlp` for DLP content | This app-only reference uses admin-consented app. Resource `https://manage.office.com`; not Graph. Enabled audit and subscription per content type required | Eligible M365 audit subscription; 7-day availability window [A5] |
| Copilot Studio transcripts (`transcripts`) | Delegated Dataverse `user_impersonation` when using a user; app-only requests use environment `/.default` with a Dataverse application user, not a Graph scope | Environment **Bot Transcript Viewer** role for human transcript access; app user must have a security role granting read access to required ConversationTranscript rows/columns in correct business scope. Environment Maker alone is insufficient | Supported Copilot Studio/Dataverse environment, recording on and transcript data present; content redactions remain [C1,C2,C3] |

Directory-wide consent can expose substantial information. Separate service
principals and trust boundaries for identity metadata, M365 interaction content,
and security investigation when possible. A 403 does not justify adding every
Graph permission.

**Audit Search documentation discrepancy:** the retrieved `get auditLogQuery`
page currently lists `ThreatIntelligence.Read.All`, while create-query and
list-records pages list `AuditLogsQuery*` permissions [A1]. The collector uses
the Audit Search workflow and the matrix reflects its intended workload
permissions; polling authorization has not been live-verified. Do **not**
automatically add an unrelated threat-intelligence grant to resolve a 403.
Validate the approved AuditLogsQuery grant in a pilot and escalate the
documentation/service discrepancy to Microsoft if polling is denied.

## Runtime submission, ingestion and administration (NOT collector grants)

| Operation | Exact permission / audience | Roles and boundaries |
|---|---|---|
| Start Management subscription (`management-start`) | Same `ActivityFeed.Read` resource permissions; DLP scope as above | Explicit feed setup; doesn't enable tenant-wide audit or create policy [A5] |
| Purview protection scope compute | `ProtectionScopes.Compute.User` least privilege, `ProtectionScopes.Compute.All` broader; both delegated/application documented, Graph resource | Use a known user's `/users/{id}` route for app-only; `/me` requires delegated user. "User" in permission name doesn't mean `/me` supports app-only [P1] |
| Purview process content | `Content.Process.User` least privilege, `Content.Process.All` broader; both delegated/application, Graph resource | Registered protected app location, appropriate policies, Purview billing. No arbitrary-user impersonation assumption; validate authorization model for the app [P2,P5] |
| Purview content activity | `ContentActivity.Write` delegated/application, Graph resource | Audit metadata submission; no policy bypass or query permission implied [P3] |
| Logs Ingestion API | Token resource `https://monitor.azure.com` / `.default`; no Graph permission | **Monitoring Metrics Publisher on the DCR**, not workspace shared key. Create table/DCR requires separate Azure management permissions; reader credentials shouldn't own infrastructure [X1] |
| Sentinel / Log Analytics querying | Azure RBAC Log Analytics Reader or scoped equivalent; querying logs API uses its documented audience, not the ingestion audience | Sentinel Reader for portal investigations as appropriate; no contributor required for read-only collection. Logs query API not implemented by this collector |
| Agent 365 observability delegated OBO | `Agent365.Observability.OtelWrite` delegated; resource `api://9b975845-388f-4429-889e-eab1ef63949c`; explicit admin consent | Token must be for observability, not bot audience; tenant/agent baggage required [S1,S2] |
| Agent 365 observability standard-app S2S | `Agent365.Observability.OtelWrite` **application** on same resource; admin consent | Standard custom-engine app; agent ID in route must match ServiceConnection ClientId. Uses `/observabilityService` [S2] |
| Registered blueprint-agent S2S | Agentic identity token chain per official instructions; not ordinary client credentials | Registered agent instance doesn't need the same observability app-role grant; don't assume standard-app S2S works for agentic apps (`AADSTS82001`). This reference does not implement that token chain [S2] |
| Generic HTTPS / Splunk HEC | Destination-specific token from approved secret provider; never reuse Microsoft source tokens | Write-only sink identity, approved TLS endpoint and index, no admin token. Generic sink contract must be implemented by receiver [X4] |
| Conditional Access administration | Separate admin account/flow; not collector identity | Conditional Access Administrator; base agent CA has P1/E3 pairing guidance, but Agent 365 agent **risk-based** CA requires Entra P2/M365 E5 or documented E7 entitlement. Risk operations need reader/admin roles [E4,E9,E11] |
| Add service principal to inventory security group | Graph `GroupMember.ReadWrite.All` **and** `Application.ReadWrite.All` | Separate privileged administration only, delegated supported group owner/directory role also required; membership does not scope agent CA [E13] |
| Purview DLP/labels/retention/CC/eDiscovery administration | Solution-specific Purview roles, not extra Graph collector permissions | Data Loss Prevention, Information Protection, Records/Data Lifecycle, Communication Compliance and eDiscovery role groups separately. Content viewer/investigator access differs from policy management [P5,P7] |
| Agent 365 CLI setup | Command-specific delegated/admin resource access; see CLI reference | Minimum setup guidance: Azure Contributor + Agent ID Developer; S2S grants Agent ID Administrator; OAuth2 grants can need a separate Global Administrator. Do not run admin consent from ordinary CI [S6] |

## Licensing procurement checklist

Confirm precise tenant offers/service plans rather than treating "E5" as a
universal answer. Audit Standard/Premium and audit-retention entitlements differ;
Microsoft 365 Copilot interaction export specifically needs its licensed
service plan. Defender hunting tables require the corresponding deployed
Defender products. Entra service principal risk streaming requires Workload ID
Premium; Entra agent risk is a distinct capability with Agent 365 licensing
guidance [E4,E7].

Conditional Access for agents currently documents Microsoft 365 E7 **or** Agent
365 plus at least Entra P1/M365 E3 [E9]. **Risk-based** agent CA has the additional
P2/M365 E5 requirement with Agent 365 (or E7) [E11]. Agent user accounts/notifications have
Frontier preview constraints [S5]. Purview Entra-registered AI-app management
requires **pay-as-you-go billing**, plus applicable solution entitlements and
roles [P5,P7]. Azure Monitor/Sentinel ingest/retention and model usage have
separate metered charges. Recheck sources at purchase/deployment time; package
release status does not establish a service licensing entitlement.
