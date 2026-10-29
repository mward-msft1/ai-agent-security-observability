# A security professional's guide to AI interactions and agent risk

## What this repository is intended to accomplish

AI assistants and agents can find information, generate answers and take
actions across business systems. Security teams need to understand **who or
what acted, which information was involved, what controls applied, and what
evidence is available when something goes wrong**.

This repository is a practical reference for building that visibility and
putting appropriate Microsoft 365 security and compliance controls around it.
It brings together documented collection examples, investigation queries,
permissions guidance and policy setup instructions. It helps security,
identity and compliance professionals turn separate product signals into a
reviewable audit trail.

It is **not a turnkey monitoring product**, an automatic tenant deployment or
a guarantee that every AI conversation can be retrieved. Use it to design and
pilot a solution appropriate to your organization's licenses, agents, data
and investigation responsibilities. This is an independent reference, not a
Microsoft product.

## The questions it helps you answer

| Security question | Evidence and guidance provided |
|---|---|
| Where are AI interactions occurring? | Microsoft 365 Copilot audit and interaction APIs, supported Copilot Studio transcripts, and instrumented custom-agent examples in the [API guide](docs/api-surfaces.md) |
| Which identity accessed our systems? | Entra agent inventory, sign-ins, directory audit and Microsoft Graph request activity; see [identity guidance](docs/entra-policies.md) |
| What data did an agent use? | Available resource references, labels and explicitly instrumented tool activity; see the [coverage matrix](docs/coverage.md), not a claim that every backend read is visible |
| Can we review prompts and responses? | Supported content retrieval/submission paths, with separate permissions, recording controls and privacy safeguards in the [SDK/content guide](docs/sdk-and-content.md) and [permissions matrix](docs/permissions.md) |
| Is an agent behaving unexpectedly? | Entra identity risk, Defender findings, Purview agent/user risk and clearly labeled investigation hypotheses in the [query library](queries/README.md) |
| Which controls should we configure? | Step-by-step [Entra Conditional Access](docs/entra-policies.md) and [Microsoft Purview DLP, Communication Compliance and Insider Risk Management](docs/m365-policy-recipes.md) runbooks |
| How do we investigate in our existing tools? | [Defender and Sentinel queries](queries/README.md), native connector guidance and [Sentinel/third-party SIEM export examples](docs/siem.md) |
| How do we preserve and review AI evidence? | [Purview eDiscovery tasks](docs/ediscovery.md): case creation, holds, AI searches, content review, export and controlled closure |

## Three layers of protection

**Identity and access: should this identity receive access?** Microsoft Entra
governs authentication and access to Entra-protected resources. Agent-risk
Conditional Access can block a high-risk agent at the supported token boundary.
An agent acting for a human, an autonomous agent identity and an agent's own
user account are different policy subjects. See [Entra setup](docs/entra-policies.md).

**Data protection: should this information be used in this interaction?**
Microsoft Purview Data Loss Prevention (DLP) can restrict supported Copilot
prompt processing, external web search or use of labeled grounding content.
Custom AI apps need their documented integration and in-application enforcement.
An audit event or telemetry exporter alone does not enforce a data policy.
See [M365 DLP recipes](docs/m365-policy-recipes.md) and
[custom-app Purview integration](docs/purview-policies.md).

**Investigation: does this activity need review?** Communication Compliance
(CC) evaluates supported communications and AI interactions for review.
Insider Risk Management (IRM) correlates supported activities and risk
indicators over time. Defender findings and Entra risk add security context.
These are different signals, not interchangeable scores or automatic proof
that a person or agent breached policy. See the [CC and IRM recipes](docs/m365-policy-recipes.md).

## Start with a controlled Microsoft 365 pilot

1. **Identify the agents and people involved.** Record each agent's purpose,
   accountable owner, hosting platform, identity/object IDs, permissions and
   data sources. Include users who interact with Copilot, not just agents.
   Check the [coverage matrix](docs/coverage.md) and [permissions](docs/permissions.md).
2. **Organize the pilot scope.** Create the security groups and separate CC
   scope described in the [Entra group and targeting instructions](docs/entra-policies.md).
   A group is useful for inventory and supported user-based policies, but it
   is **not a universal agent-policy scope**.
3. **Establish the audit trail first.** Confirm [Purview auditing](docs/purview-policies.md)
   and the appropriate [Entra diagnostic logs](docs/entra-policies.md).
   Use [synthetic examples](docs/quickstart.md) to check that the expected records
   arrive before relying on them.
4. **Configure access controls.** Follow the [Entra runbook](docs/entra-policies.md)
   to target agent identities, blueprints or attributes. Start the high-agent-risk
   block policy in Report-only. Use a separate policy for agent user accounts and
   separate human-user policies for delegated access.
5. **Configure Microsoft 365 data policies.** Follow the
   [M365 policy recipes](docs/m365-policy-recipes.md) for Copilot DLP, CC review and
   IRM. Use DLP simulation, a small licensed pilot and approved synthetic
   positive/negative controls before broad enforcement.
6. **Bring the evidence into investigations.** Use the [query library](queries/README.md)
   and [SIEM guidance](docs/siem.md). Map identifiers carefully, restrict content
   access, and define an incident-response and evidence-retention process.
   For authorized content investigations, follow the
   [eDiscovery runbook](docs/ediscovery.md) to preserve, search, review and export
   available interactions and relevant files.
7. **Extend to custom and third-party agents.** Add supported
   [SDK instrumentation](docs/sdk-and-content.md) and
   [Purview integration](docs/purview-policies.md) where available.
   Non-Microsoft hosting is not itself a barrier, but missing integration
   cannot be fixed by a query.

### Important: security groups do not make all these scopes equivalent

An agent's service principal, its optional agent user account, and the human
who prompts it are separate directory objects. A policy scoped to one does
not automatically protect the others. Microsoft's current agent CA guidance
does **not** support agent-user group-membership targeting, and ordinary
user/group assignments do not protect agent user accounts. For autonomous
agents use **Agents** targeting, not the group's name in a Users assignment.
The [Entra runbook](docs/entra-policies.md) explains the supported alternatives.

Likewise, a service-principal inventory group is not a Purview CC or IRM user
scope. CC supports particular mail-enabled group types and individual
reviewers. IRM's user-focused Risky AI usage and agent-focused Risky Agents
policies have different subjects and prerequisites. See [M365 scope requirements](docs/m365-policy-recipes.md).

## What you receive

The repository includes runnable reference collectors, synthetic fixtures,
a per-operation permissions matrix, 12 investigation queries, SIEM export
examples, SDK instrumentation examples and CI/CD checks. Customer runbooks
explain audit, licensing, scoped rollout, validation and rollback. Product
claims link to a [source catalog](docs/sources.md); beta/preview dependencies and
known gaps are called out explicitly.

| Need | Direct reference |
|---|---|
| Know what can actually be captured | [Coverage, retention/latency and limitations](docs/coverage.md) |
| Run a bounded collection or resume after failure | [Quickstart and operation examples](docs/quickstart.md), [Python collectors](agent_audit/collect.py) |
| Obtain the right permissions without blanket admin access | [OAuth, audience, RBAC and licensing matrix](docs/permissions.md) |
| Understand Graph security vs other Graph/Purview APIs | [API families and raw HTTP examples](docs/api-surfaces.md) |
| Hunt available activity and signals | [12 Defender/Sentinel KQL examples and prerequisites](queries/README.md) |
| Send available records to a SIEM | [Sentinel and third-party export runbook](docs/siem.md), [custom DCR](config/dcr.json) |
| Create security groups and configure agent access controls | [Entra governance and Conditional Access](docs/entra-policies.md) |
| Configure Microsoft 365 Copilot DLP, CC and IRM | [Step-by-step M365 policy recipes](docs/m365-policy-recipes.md) |
| Preserve, investigate and produce AI evidence | [eDiscovery case, hold, search, review and export tasks](docs/ediscovery.md) |
| Configure audit, custom-app collection, labels and retention | [Purview policy runbook](docs/purview-policies.md) |
| Instrument code and retain approved prompts/responses | [Framework, Agent 365 SDK/CLI and OTel guide](docs/sdk-and-content.md), [runnable examples](examples) |
| Add observability checks to development pipelines | [CI/CD guidance](docs/cicd.md), [GitHub Actions](.github/workflows), [Azure Pipelines](azure-pipelines.yml) |
| Check evidence and provenance | [Sources, versions and prior art](docs/sources.md), [validation record](docs/validation.md) |

Operational metadata is retained by default. Full raw-content storage needs
both `--include-content` and `CONTENT_CAPTURE_APPROVED=true`, and can include
sensitive identifiers and resource links as well as messages. Set access,
minimization, encryption, retention and legal review requirements **before**
enabling content collection. Read [data handling](SECURITY.md) first; some APIs
return content over the network even when the collector does not persist it.

### Try the offline examples

Follow the [technical quickstart](docs/quickstart.md) for installation, then:

```powershell
python -m agent_audit.cli fixture
python -m agent_audit.cli export --file .local\synthetic.jsonl
python -m unittest discover -s tests -v
```

No tenant, subscription, secret, model or cloud deployment is needed for these
offline examples.

## What success looks like

A successful pilot can identify a synthetic interaction and its identity,
locate the relevant audit/resource-access evidence, demonstrate the intended
policy outcome, and explain any missing signal. Investigators can distinguish
**an actual product detection**, **a policy match**, **a blocked action**, and
**an analytic lead**. The team knows who responds, which evidence they can
access and how long each copy is retained.

Do not treat one successful trace or audit query as proof of complete coverage.
Audit metadata is not necessarily prompt text; identity risk is not content
risk; a CC/IRM alert is not an inline block. Live tenant outcomes must be
validated against the [coverage matrix](docs/coverage.md), [permissions](docs/permissions.md)
and [acceptance checklist](docs/validation.md).

## Status and boundaries

Research baseline: **2026-10-28**. Microsoft Learn pages and Microsoft-owned
upstream repositories are the authority; user repositories informed scenarios
only. Source-specific maturity and preview gates are documented per example.
Commercial cloud is the implemented default; sovereign clouds require separate
endpoint, permission and availability validation.

Offline behavior is tested; live tenant policies, connectors, content export,
model invocation and ingestion require customer prerequisites and are **not
claimed executed**. This repository does not automatically apply policies or
provision live resources. See [validation](docs/validation.md) before deployment.
