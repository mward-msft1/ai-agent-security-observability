# Validation record and customer acceptance checklist

Validation host: **Windows, Python 3.14.7**, SDK packages from the resolved lock,
.NET SDK **10.0.401**, pinned Agent 365 CLI **2.0.1+97997c7849**.
Research baseline 2026-10-28; final checks 2026-10-29 UTC.

## Executed locally

Final local result: **37 passed, 1 skipped live test** (38 total) in the SDK
environment; **33 passed, 5 explicitly skipped** in the clean base-only
environment (four SDK checks plus live). All structure/schema/citation checks
passed: **12 KQL files, 49 source IDs, 2 GitHub workflow structures**.
Both environments passed `pip check`; the collector wheel built successfully.
Pinned CLI restore/version/setup-query help succeeded. The fixture CLI imported
the same fixture twice and exported **one** metadata-only record, proving replay
deduplication. pip-audit 2.9.0 completed with **"No known vulnerabilities found"**
for the SDK lock; it warned that the fully pinned lock is not hash-locked.
This result is time-bound advisory evidence, not a vulnerability-free guarantee.

Tests use
synthetic fixtures, fake HTTPS responses and isolated temporary SQLite files;
no actual tenant interaction payloads are persisted.

| Check | Scope / expected evidence |
|---|---|
| `python -m unittest discover -s tests -v` | Collectors, atomic checkpoint replay/dedup, throttling/Retry-After, endpoint rejection, actual auth header, Audit Search polling/error/resume, Management page headers/blobs, outbox errors/ack, fail-closed Purview decisions; SDK import/constructor and content-off/on real spans |
| `python scripts\validate_repository.py` | Python syntax, JSON schema/fixture types, Markdown relative links/source IDs, KQL shape and YAML/action pin structure |
| `python -m pip check` | Installed dependency consistency |
| `python -m pip wheel --no-deps --wheel-dir .local\wheel .` | Build installable collector wheel |
| `dotnet tool restore`; `dotnet a365 --version`; command `--help` | Actual pinned CLI availability/command tree, **not** tenant setup |
| Fixture CLI -> SQLite -> JSONL, repeated import | Default metadata-only CLI round trip, stable dedup |
| `python -m pip_audit --no-deps --disable-pip --strict -r requirements-sdk.lock` | Public dependency advisory service; separate from offline correctness checks |

Action versions were checked against actual upstream release/tag objects and
action manifests, then pinned to commit SHAs: checkout **v7.0.1**, setup-python
**v7.1.0**, azure/login **v3.1.0**. The annotated Azure login tag was dereferenced
to its commit. These actions use Node 24; `windows-latest` is the intended
supported hosted-runner target. Local YAML checking doesn't execute their code.

## Hosted GitHub Actions verification

The [implementation validation run](https://github.com/mward-msft1/ai-agent-security-observability/actions/runs/40800359548)
at commit `1e5cc4ab9ee86de54e12c0cd89f4ee3003e8587e` completed **successfully**.
Both clean Windows hosted jobs passed: base collector tests/schema/wheel/
dependency advisory/CLI restore-version checks, and pinned SDK install/
dependency consistency/real offline span checks. This is actual hosted
execution, not inferred from YAML syntax. No live tenant job was dispatched.

SDK console tests forbid socket connects and assert a real invocation span
exists. They also assert the synthetic prompt/response is absent by default
and present only in opt-in mode. This avoids passing a no-op instrumentation
demo as validated. Unused OpenAI Agents auto-instrumentation and SDK
statistics are disabled in this console demo; no optional OpenAI Agents
package is installed solely to hide its import warning.

## Not executed / not established

- **All live tenant operations**: Graph/Purview queries, interaction retrieval,
  Dataverse transcript read, risky-agent/Agent ID beta calls, model inference,
  Agent 365/Purview/Azure Monitor network ingestion, HEC/generic SIEM delivery,
  policies, connectors, consent, billing and CLI setup/deployment.
- The live read test is **explicitly skipped** without its approval flag.
  SDK tests are also explicitly skipped in a base-only environment; final
  local SDK results use the environment where pinned SDKs are actually installed.
- Azure Pipelines execution, the manual live-read GitHub workflow and GitHub
  Environment protection behavior remain unverified. The hosted offline/SDK
  GitHub run above is the only pipeline execution claimed here.
- No live KQL semantic/schema binding. Structural checks are not a Kusto
  compiler. Each native table needs its documented connector/product. Native
  CopilotActivity cannot be a custom Logs Ingestion API destination.
- No universal content completeness, latency SLA, end-to-end redaction
  guarantee, beta production support, multi-cloud sovereign availability,
  exactly-once delivery or Splunk indexer acknowledgement.
- Audit Search polling docs currently conflict on permissions; see
  [the explicit discrepancy](permissions.md). Pilot authorization is required.

## eDiscovery documentation revision (2026-10-29)

The [eDiscovery runbook](ediscovery.md) was checked against directly fetched
Microsoft guidance for AI item classes, roles, holds, searches, review sets,
exports, Pages containers and billing. Documentation-only checks passed for
**17 Markdown files, 66 source IDs, 126 relative links** and balanced code
fences; `git diff --check` passed.

At the time of the eDiscovery documentation revision, the full repository
validator stopped with
`ValueError: Direct SDK requirements must match the resolved lock`.
The existing dependency update on `main` selects
`agent-framework-core==1.23.0` in `requirements-sdk.txt`, while
`requirements-sdk.lock` still pins 1.22.0. This mismatch predates the
eDiscovery revision and is not repaired by this documentation-only change.
The targeted documentation checks do not establish dependency consistency.
The mismatch was subsequently resolved by aligning the direct requirement to
the available, tested 1.22.0 package; see the SDK pin alignment follow-up below.

No eDiscovery case, hold, search, collection, export, purge or billing setup
was executed against a live tenant. Customer acceptance tasks are provided
at the end of the runbook.

## Supplied-source verification follow-up (2026-10-28)

The user-supplied Microsoft Learn and Microsoft-owned GitHub references were
fetched and checked against the Entra, Graph security, Purview, Agent 365,
Microsoft OpenTelemetry, Agent Framework and PowerShell guidance. Relevant
additions/corrections are linked in [the source catalog](sources.md): human
passkeys versus agent identity controls; optional sidecar trust-boundary
requirements; the registered Agent 365 S2S `/otlp` route/token distinction;
Purview's Agent Framework developer references; Graph security broker/beta
scope; Security & Compliance versus Exchange Online PowerShell sessions; and
the unified Microsoft OpenTelemetry Distro's supported languages and
multi-destination setup, distinct from initializing a separate Azure Monitor
provider.

Documentation checks passed for citations and relative links with **77 source
IDs**. At the time of this check, the direct requirement/lock discrepancy
remained: the manifest requested framework core 1.23.0 while lock/tests used
1.22.0. The configured package feed does not publish 1.23.0, so the manifest
was aligned to the available, tested 1.22.0 pin. Follow-up validation results
are recorded below. No live tenant authentication, observability export,
policy, Purview or Graph operation was performed for this research pass.

## SDK pin alignment follow-up (2026-10-29)

The configured package feed returned no distribution for
`agent-framework-core==1.23.0` (available versions ended at 1.22.0). The direct
manifest was changed back to 1.22.0 to match the checked-in lock and previously
tested package set; no transitive lock changes were needed. The repository
validator passed; the SDK/collector suite passed **37 tests** with the live
tenant test explicitly skipped, and `pip check` found no broken requirements.

## Customer acceptance before production

Documentation follow-up: the customer overview and M365 policy recipes add
verified group-type/CA-targeting boundaries, native Copilot DLP, CC and IRM
procedures, and the separate Risky Agents preview. Repository structure/link/
citation checks passed with **57 source IDs**, 12 unchanged query files and
two workflow structures. This update changes no runtime code and creates no
live groups or policies; the portal procedures remain customer pilot steps.

1. Select the applicable [coverage row](coverage.md), approve exact source/
   destination permissions, test native schema and retain the evidence.
2. Use fixed synthetic prompt/response and resource-access positive/negative
   controls. Verify the default path doesn't retain content, then separately
   authorize any content path and confirm actual downstream presence/redaction.
3. Validate source identity mapping and correlation, not just approximate
   timestamps. An audit ThreadId, service principal object ID, app ID, native
   agent version ID and trace OperationId are not interchangeable.
4. Test page interruption, late arrivals/overlap, 429/Retry-After, revoked auth,
   missing service entitlements, oversized events, destination failure and replay.
5. Test inline allow/block and policy/API failure **before** downstream action;
   verify actual resource enforcement, policy event and expected retention.
6. Confirm SIEM reconciliation/dedup, backlog alerting and restricted
   dead-letter handling; deploy approvals and rollback per runbooks.
7. Record source versions, tenant feature rollout/licenses, measured latency,
   reviewer roles and deletion/hold behavior. Revalidate on dependency/API
   upgrades rather than asserting fixture success proves live support.
