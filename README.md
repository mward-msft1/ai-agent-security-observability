# AI agent security, audit, and observability reference

Customer examples for collecting **first-party and instrumented third-party AI
agent activity**, investigating it, and routing available evidence to Microsoft
Sentinel or another SIEM. This is an independent reference repository, not a
Microsoft product or a promise to capture every agent interaction.

**New to this reference? Read the [customer guide](docs/customer-guide.md)** for
its purpose, security outcomes and recommended pilot. For policy setup, use the
[Microsoft 365 DLP, CC and IRM recipes](docs/m365-policy-recipes.md) and
[Entra security-group and agent CA instructions](docs/entra-policies.md).

Then read [coverage and genuine gaps](docs/coverage.md) and use the
[offline quickstart](docs/quickstart.md). No tenant, subscription, secret, model,
or cloud deployment is needed for the offline examples.

```powershell
python -m agent_audit.cli fixture
python -m agent_audit.cli export --file .local\synthetic.jsonl
python -m unittest discover -s tests -v
```

Default persistence is metadata-only. Full raw content retention requires both
`--include-content` and `CONTENT_CAPTURE_APPROVED=true`; read
[data handling](SECURITY.md) first. Some source APIs return content over the
network even when this collector does not persist it.

## What is here

| Need | Deliverable |
|---|---|
| Know what can actually be captured | [Coverage, retention/latency and limitations](docs/coverage.md) |
| Run a bounded collection or resume after failure | [Quickstart and operation examples](docs/quickstart.md), [Python collectors](agent_audit/collect.py) |
| Obtain the right permissions without blanket admin access | [Per-operation OAuth, audience, RBAC and licensing matrix](docs/permissions.md) |
| Understand Graph security vs other Graph/Purview APIs | [API families and raw HTTP examples](docs/api-surfaces.md) |
| Hunt available activity and signals | [12 Defender/Sentinel KQL examples and prerequisites](queries/README.md) |
| Send available records to a SIEM | [Sentinel, Event Hubs/storage and third-party export runbook](docs/siem.md), [custom DCR](config/dcr.json) |
| Configure identity controls | [Entra governance and Conditional Access runbook](docs/entra-policies.md) |
| Configure audit, collection, DLP, labels and retention | [Purview policy runbook](docs/purview-policies.md) |
| Instrument code and retain approved prompts/responses | [Framework, Agent 365 SDK/CLI and OTel guide](docs/sdk-and-content.md), [runnable examples](examples) |
| Add observability checks to development pipelines | [CI/CD guidance](docs/cicd.md), [GitHub Actions](.github/workflows), [Azure Pipelines](azure-pipelines.yml) |
| Check evidence and provenance | [Source catalog, exact versions and prior-art review](docs/sources.md), [validation record](docs/validation.md) |

## Boundaries that matter

**Audit metadata is not conversation content.** Copilot audit events can contain
message IDs and accessed-resource references, not the prompt/answer text.
The licensed Microsoft 365 Copilot interaction export API is a different API;
it explicitly excludes interactions in agents created with Copilot Studio.
Copilot Studio transcripts have their own permissions, recording controls and
documented redactions.

**Identity is not interaction telemetry.** Sign-ins show token/access context;
they do not show every tool call, prompt or response. Inventory synchronization
does not instrument a third-party runtime.

**Observation is not enforcement.** Azure Monitor tracing alone is not Purview
compliance ingestion. Purview runtime API policy actions must be honored by
the application before the relevant model/tool/delivery boundary. Volume or
keyword heuristics in this library are labeled hypotheses, not confirmed policy
violations or product risk detections.

## Status

Research baseline: **2026-10-28**. Microsoft Learn pages and Microsoft-owned
upstream repositories are the authority; user repositories informed scenarios
only. Source-specific API maturity and preview gates are documented per example.
Commercial cloud is the implemented default; sovereign clouds require separate
endpoint, permission and availability validation.

Offline behavior is tested; live tenant policies, connectors, content export,
model invocation and ingestion require customer prerequisites and are **not
claimed executed**. This repository does not automatically apply policies or
provision live resources. See [validation](docs/validation.md) before deployment.
