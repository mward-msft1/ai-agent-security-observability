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
and investigation responsibilities.

## The questions it helps you answer

| Security question | Evidence and guidance provided |
|---|---|
| Where are AI interactions occurring? | Microsoft 365 Copilot audit and interaction APIs, supported Copilot Studio transcripts, and instrumented custom-agent examples |
| Which identity accessed our systems? | Entra agent inventory, sign-ins, directory audit and Microsoft Graph request activity |
| What data did an agent use? | Available resource references, labels and explicitly instrumented tool activity; not a claim that every backend read is visible |
| Can we review prompts and responses? | Supported content retrieval/submission paths, with separate permissions, recording controls and privacy safeguards |
| Is an agent behaving unexpectedly? | Entra identity risk, Defender findings, Purview agent/user risk and clearly labeled investigation hypotheses |
| Which controls should we configure? | Step-by-step Entra Conditional Access and Microsoft Purview DLP, Communication Compliance and Insider Risk Management runbooks |
| How do we investigate in our existing tools? | Defender and Sentinel queries, native connector guidance and custom export examples for Sentinel/third-party SIEMs |

## Three layers of protection

**Identity and access: should this identity receive access?** Microsoft Entra
governs authentication and access to Entra-protected resources. Agent-risk
Conditional Access can block a high-risk agent at the supported token boundary.
An agent acting for a human, an autonomous agent identity and an agent's own
user account are different policy subjects.

**Data protection: should this information be used in this interaction?**
Microsoft Purview Data Loss Prevention (DLP) can restrict supported Copilot
prompt processing, external web search or use of labeled grounding content.
Custom AI apps need their documented integration and in-application enforcement.
An audit event or telemetry exporter alone does not enforce a data policy.

**Investigation: does this activity need review?** Communication Compliance
(CC) evaluates supported communications and AI interactions for review.
Insider Risk Management (IRM) correlates supported activities and risk
indicators over time. Defender findings and Entra risk add security context.
These are different signals, not interchangeable scores or automatic proof
that a person or agent breached policy.

## Start with a controlled Microsoft 365 pilot

1. **Identify the agents and people involved.** Record each agent's purpose,
   accountable owner, hosting platform, identity/object IDs, permissions and
   data sources. Include users who interact with Copilot, not just agents.
2. **Organize the pilot scope.** Create the security groups and separate CC
   scope described in the [Entra group and targeting instructions](entra-policies.md).
   A group is useful for inventory and supported user-based policies, but it
   is **not a universal agent-policy scope**.
3. **Establish the audit trail first.** Confirm Purview auditing and the
   appropriate Entra diagnostic logs. Use synthetic interactions to check
   that the expected records arrive before relying on them.
4. **Configure access controls.** Follow the Entra runbook to target agent
   identities, blueprints or attributes. Start the high-agent-risk block
   policy in Report-only. Use a separate policy for agent user accounts and
   separate human-user policies for delegated access.
5. **Configure Microsoft 365 data policies.** Follow the
   [M365 policy recipes](m365-policy-recipes.md) for Copilot DLP, CC review and
   IRM. Use DLP simulation, a small licensed pilot and approved synthetic
   positive/negative controls before broad enforcement.
6. **Bring the evidence into investigations.** Use the [query library](../queries/README.md)
   and [SIEM guidance](siem.md). Map identifiers carefully, restrict content
   access, and define an incident-response and evidence-retention process.
7. **Extend to custom and third-party agents.** Add supported instrumentation
   and Purview integration where available. Non-Microsoft hosting is not
   itself a barrier, but missing integration cannot be fixed by a query.

### Important: security groups do not make all these scopes equivalent

An agent's service principal, its optional agent user account, and the human
who prompts it are separate directory objects. A policy scoped to one does
not automatically protect the others. Microsoft's current agent CA guidance
does **not** support agent-user group-membership targeting, and ordinary
user/group assignments do not protect agent user accounts. For autonomous
agents use **Agents** targeting, not the group's name in a Users assignment.
The [Entra runbook](entra-policies.md) explains the supported alternatives.

Likewise, a service-principal inventory group is not a Purview CC or IRM user
scope. CC supports particular mail-enabled group types and individual
reviewers. IRM's user-focused Risky AI usage and agent-focused Risky Agents
policies have different subjects and prerequisites.

## What you receive

The repository includes runnable reference collectors, synthetic fixtures,
a per-operation permissions matrix, 12 investigation queries, SIEM export
examples, SDK instrumentation examples and CI/CD checks. Customer runbooks
explain audit, licensing, scoped rollout, validation and rollback. Product
claims link to a [source catalog](sources.md); beta/preview dependencies and
known gaps are called out explicitly.

Operational metadata is retained by default. Full raw-content storage needs
explicit approval, and can include sensitive identifiers and resource links
as well as messages. Set access, minimization, encryption, retention and legal
review requirements **before** enabling content collection.

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
validated against the [coverage matrix](coverage.md), [permissions](permissions.md)
and [acceptance checklist](validation.md).

**Next reading:** [Microsoft 365 policy recipes](m365-policy-recipes.md),
[Entra setup](entra-policies.md), [custom-app Purview integration](purview-policies.md),
then the [technical quickstart](quickstart.md).
