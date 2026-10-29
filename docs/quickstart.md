# Run collectors and replay safely

Use Python 3.11+ for the stdlib-only collector. Tested SDK pins and environment
details are in [validation](validation.md). Commands below use PowerShell and
run from the repository root. Read [permissions](permissions.md) and
[data handling](../SECURITY.md) before any live request.

## 1. Offline first (no authentication)

```powershell
python -m agent_audit.cli --db .local\demo.sqlite fixture
python -m agent_audit.cli --db .local\demo.sqlite fixture
python -m agent_audit.cli --db .local\demo.sqlite export --file .local\demo.jsonl
python -m unittest discover -s tests -v
```

The second fixture run is deduplicated. Output has one normalized synthetic
Copilot audit event, counts of resource references/messages, no prompt content
and no sensitive resource URLs. This fixture establishes plumbing, not live coverage.

## 2. Authenticate only the operation you need

The core has no dependencies. For Azure CLI credential refresh or federated
workload auth, install the pinned optional Azure identity dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[azure]"
```

Use `--auth cli` only after a deliberate `az login --tenant YOUR_TENANT` using an
approved account/application; Azure CLI login does not itself consent the
collector permissions. `--auth workload` uses **WorkloadIdentityCredential** and
`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_FEDERATED_TOKEN_FILE`, not a broad
default-credential fallback. This supports an AKS/projected federated assertion
when configured. GitHub's azure/login instead authenticates Azure CLI, so its
example uses `--auth cli`.

The default `--auth environment` reads `ACCESS_TOKEN` and never refreshes it.
Obtain it through your approved identity library/secret provider for the
specific resource in the matrix. Don't put tokens in arguments, committed
files or shell output. A 401 is a failure, not a reason to fall back to another
user/tenant. Static tokens are suitable only for short development probes.

## 3. Collect metadata from documented Graph profiles [A1,A3,D1-D3,E1-E6]

```powershell
$start = "2026-10-27T00:00:00Z"
$end = "2026-10-28T00:00:00Z"
python -m agent_audit.cli --auth cli audit --start $start --end $end
python -m agent_audit.cli --auth cli graph --profile directory-audit --start $start --end $end
python -m agent_audit.cli --auth cli graph --profile signins --start $start --end $end
python -m agent_audit.cli --auth cli graph --profile alerts --start $start --end $end
python -m agent_audit.cli --auth cli graph --profile incidents --start $start --end $end
python -m agent_audit.cli --auth cli graph --profile service-principals --start $start --end $end
```

`audit` creates a **saved search job** in Purview via Graph security, polls up to
10 minutes, then pages records. It defaults to `CopilotInteraction`; use
`--operation connectedAIAppInteraction` for the documented custom-app operation
where configured. This is a query-job creation, not a policy/data write.
On timeout rerun the identical operation/window/db to resume the saved job.
If the create response is lost, inspect saved queries before resubmitting;
POST creation is intentionally not automatically retried.

Inventory/risky state are current snapshots, not time-filtered histories;
start/end are accepted for consistent CLI shape but do not filter snapshots:

```powershell
python -m agent_audit.cli --auth cli graph --profile agent-identities --allow-beta --start $start --end $end
python -m agent_audit.cli --auth cli graph --profile risky-agents --allow-beta --start $start --end $end
```

Beta use is explicit; review production restrictions. Ordinary service
principals aren't automatically AI agents. Map your curated application IDs
and Agent ID inventory, not display-name keywords.

## 4. Retrieve licensed M365 Copilot interaction records [A3]

Use an **application token** with `AiEnterpriseInteraction.Read.All`; delegated
CLI user tokens are not supported for this endpoint. Supply a curated list of
licensed user object IDs, not an unreviewed full directory enumeration.

```powershell
python -m agent_audit.cli graph --profile interactions --user USER_OBJECT_ID --start $start --end $end
```

By default only allowed metadata is retained. The API may still return content
in memory; permission/approval is required even if it is immediately discarded.
For explicitly approved content persistence, use a **separate database**:

```powershell
$env:CONTENT_CAPTURE_APPROVED = "true"
python -m agent_audit.cli --db .local\restricted-content.sqlite --include-content graph --profile interactions --user USER_OBJECT_ID --start $start --end $end
Remove-Item Env:\CONTENT_CAPTURE_APPROVED
```

Do not treat this local flag as authorization. The retained `Data.Raw` contains
the full response record (including cards/attachments if returned), not a
sanitized prompt/response projection. Copilot Studio agents are excluded.
The documented time filter uses strict `gt` and `lt`; overlap adjacent windows
to cover exact boundaries and late arrivals.

## 5. Office 365 Management Activity API [A5]

Use a **different token** for `https://manage.office.com`. An authorized
administrator first enables the subscription explicitly:

```powershell
python -m agent_audit.cli management-start --tenant TENANT_ID --content-type Audit.General
python -m agent_audit.cli management --tenant TENANT_ID --content-type Audit.General --start $start --end $end
```

Update the example dates to the last seven days; windows must be <=24 hours and
not in the future. List filtering is on content availability, not event creation.
`Audit.General` is relevant to Copilot audit; collect other subscribed content
types separately as needed. `DLP.All` additionally needs `ActivityFeed.ReadDlp`.
New subscriptions can take time to produce content; existing historic data
isn't backfilled just by starting one. No webhook is required for this polling example.

## 6. Defender advanced hunting [D3,K1]

```powershell
python -m agent_audit.cli --auth cli hunting --query queries\defender\copilot-metadata.kql --start $start --end $end
```

KQL `ago()` in the example and API Timespan are intersected; edit the query
appropriately for historical backfills. Hunting isn't OData pagination. Narrow
time ranges to stay under result/CPU/size limits; the collector refuses a
100,000-row result rather than claim complete export. Metadata-only mode does
not retain arbitrary query result columns. To retain returned query rows use
the separate restricted-content store and explicit opt-in.

## 7. Copilot Studio Dataverse transcripts [C1,C2]

Get the environment's actual Web API origin from Power Platform admin center.
This is not a Microsoft Graph token audience.

```powershell
python -m agent_audit.cli transcripts --environment https://YOUR_ORG.crm.dynamics.com --start $start --end $end
```

Default selection excludes content/metadata columns. Approved raw content mode
adds them and persists records in `Data.Raw`; the collection filters `modifiedon`
and `schematype eq 'powervirtualagents'`. Confirm this schema type in the target
environment. Page and merge transcript batches by their documented conversation
and batch keys; do not join by display name. Documented `REDACTED` answers cannot
be recovered by asking Graph instead.

## Checkpoint and delivery semantics

Each OData page is committed atomically with its next-link cursor. A rerun
resumes a failed page; completed windows are re-read so delayed records can
appear. Keep a scheduler-owned window ledger and replay recent overlapping
windows (for example 48 hours for audit, adjusted to measured latency); the
Management feed must remain within its seven-day limit. This library does
not auto-invent a universal watermark for services with different clocks.

Normalized `RecordId` hashes source, namespace/user, native ID and canonical raw
record hash **and content projection mode**. Identical replay deduplicates;
changed alert/risk snapshots create
new versions. Store source `Data.NativeId` for investigation. Different API
families reporting the same activity are **not cross-source deduplicated**.

Use one worker per SQLite database, on encrypted/restricted storage. Monitor
exit code, stale windows, API throttling and queue age. POST query creation
and Purview submission aren't retried automatically on ambiguous failures.
GET/hunting/read and sink requests have bounded retries, timeout and
Retry-After handling. HTTP 401/403/other errors and invalid schema fail loudly.
Export uses per-destination acknowledgement but remains **at-least-once** after
timeouts/crashes: downstream deduplication by RecordId is required.
