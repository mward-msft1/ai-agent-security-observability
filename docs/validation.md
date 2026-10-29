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
- GitHub Actions/Azure Pipelines remote execution and GitHub Environment
  protection behavior are not inferred from local YAML validation.
- No live KQL semantic/schema binding. Structural checks are not a Kusto
  compiler. Each native table needs its documented connector/product. Native
  CopilotActivity cannot be a custom Logs Ingestion API destination.
- No universal content completeness, latency SLA, end-to-end redaction
  guarantee, beta production support, multi-cloud sovereign availability,
  exactly-once delivery or Splunk indexer acknowledgement.
- Audit Search polling docs currently conflict on permissions; see
  [the explicit discrepancy](permissions.md). Pilot authorization is required.

## Customer acceptance before production

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
