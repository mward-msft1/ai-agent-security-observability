# CI/CD for instrumented and policy-integrated agents

Build-time checks do not prove tenant onboarding, content retention or inline
policy enforcement. Keep **offline**, **privileged bootstrap** and **approved
live smoke** stages separate. This repository deploys no policies/resources.
Federation references: [X5](sources.md).

## GitHub Actions

[validate.yml](../.github/workflows/validate.yml) runs two Windows/Python 3.14
jobs with read-only repository permissions and immutable verified action SHAs:

1. Base collectors: install pinned build/dev dependencies, run unit/fixture
   tests, structure/citation/schema validation, build a wheel.
2. SDK job: restore resolved package pins, `pip check`, run the same tests plus
   actual SDK constructor/manual span checks, verify content absent by default
   and synthetic content only when explicitly selected. Socket connection
   attempts are forbidden during the console smoke test.

The base job installs **pip-audit 2.10.1** from `requirements-dev.txt` and runs it against public resolved SDK
package names/versions using its PyPI advisory service (network required).
It fails on advisories or unavailable package evidence with `--strict`;
it never sends private code, spool or interaction data. This advisory check is
not an offline check and isn't a guarantee of zero exploitable vulnerabilities.

Base tests explicitly skip SDK cases when packages are absent. Live tenant
tests explicitly skip unless enabled. Neither is silently reported as executed.

[live-read.yml](../.github/workflows/live-read.yml) is **workflow_dispatch only**,
default branch only, with an explicit approval input and a
`tenant-read-smoke` GitHub Environment. It reads at most one directory-audit
record, asserts shape and never prints/stores response content.

### Configure OIDC before enabling live read

1. Create a dedicated read-only Entra app/service principal. Approve only
   application `AuditLog.Read.All` for this smoke operation; administrator
   consent is an out-of-band setup, not an action performed by the workflow.
2. Add a federated credential with GitHub issuer
   `https://token.actions.githubusercontent.com`,
   audience `api://AzureADTokenExchange`,
   subject `repo:OWNER/REPOSITORY:environment:tenant-read-smoke`.
   Substitute the exact private repository name; don't use a wildcard subject.
3. Configure the GitHub Environment with **required reviewers**, deployment
   branch protection and the variables `AZURE_READ_CLIENT_ID`,
   `AZURE_TENANT_ID`. These identifiers aren't secrets; don't store tokens.
   Environment protections depend on GitHub plan/repository support. If your
   plan cannot enforce approval for this private repo, don't enable the live
   workflow until a supported external approval control is in place.
4. `azure/login` obtains an ephemeral federated login. `AzureCliCredential`
   requests a **Graph** token, not an ARM/Monitor token. No Azure subscription
   Contributor role is needed for directory audit read.
5. Dispatch only after reviewers approve the tenant operation. Review the
   result without uploading logs/artifacts containing the returned row.
6. Remove federation/consent or disable workflow/environment on rollback.

Don't run these jobs against untrusted PR code with tenant credentials; don't
use `pull_request_target` to execute contributions. Content capture and policy
creation never run in this workflow.

## Azure Pipelines

[azure-pipelines.yml](../azure-pipelines.yml) performs the offline SDK/tests/
schema/wheel checks on Windows. Every PowerShell native-command failure is
propagated; there's no successful final command hiding an earlier failure.
Microsoft task versions are major-version managed by Azure DevOps (not GitHub
Action commit SHAs).

For an optional live stage, configure an **Azure Resource Manager workload
identity federation service connection** using current Azure DevOps setup
[X5]. Don't replace it with a stored client secret. Require environment/service
connection checks and approvals and prevent PR execution. Grant only the
needed Graph application role out of band to the service principal used by
that connection. In an approved `AzureCLI@2` task with that named connection,
run `test_live.py` with `RUN_LIVE_READ_TESTS=true`, `LIVE_AUTH_MODE=cli`.
Use an existing isolated Python environment with `.[azure]` installed. This
optional live stage is **not pre-enabled** because a repository cannot
configure your tenant's connection identity or approval authority.

## Integrate an agent build and deployment

1. Install the exact tested Agent Framework/distro dependencies from the lock.
   Do not add deprecated Agent 365 observability packages. The CLI tool
   manifest pins the independently bootstrapped tool.
2. Add tests around every model/tool boundary: correlation propagation,
   resource-access authorization, content absence, cancellation/failure,
   and durable policy verdict handling. Use only synthetic fixtures offline.
3. Verify `compute -> processContent` for prompts before model/tool calls and
   for applicable response scopes before delivery. Test inline allow/block,
   unknown/changed scopes, malformed response, missing content-policy setup,
   throttling and timeouts. Offline evaluation doesn't satisfy a blocking gate.
4. In a separate approved nonproduction environment, provision identity/
   observability destination and Purview collection/DLP policies using the
   runbooks. Never run CLI `setup all` or tenant-wide grants on each PR.
5. Deploy the agent artifact through your existing federated deployment
   mechanism and environment approvals. This reference has no customer agent
   host/IaC deployment target to fabricate.
6. After deployment, run an authorized synthetic end-to-end canary. Require:
   real trace arrival with expected identity/correlation, no content in
   default traces, expected Audit/Purview events after measured latency,
   inline positive/negative policy result, actual blocked downstream action,
   and SIEM arrival/dedup. Keep a bounded polling deadline and fail explicitly
   when a required source is missing.
7. Release only after service-specific checks succeed; rollback the agent
   artifact/config on failure, preserving investigation data. A successful
   CLI exit or trace flush alone is not the acceptance test.

No example workflow performs model inference, Purview submission, HEC ingestion
or tenant policy changes. Those require separate permissions, billing and
review and remain unexecuted in this reference delivery.

## Dependency, secret and query checks

- Dependabot covers Python/action update proposals. Regenerate the SDK lock in
  an isolated environment, inspect diff/transitive licenses and run offline
  plus approved live checks before merging an upgrade. Dependabot isn't
  proof of zero vulnerabilities.
- Enable GitHub dependency graph, Dependabot alerts and secret scanning/push
  protection where your private-repository plan supports them. Add your
  organization's approved SCA/CodeQL/SAST gate with the required entitlement.
  Do not silently skip a mandatory enterprise gate when licensing is absent.
- Pin Actions to reviewed SHAs and protect workflow changes with code review.
  Protect the lock/manifests and identity/policy configuration similarly.
- `scripts/validate_repository.py` checks Python syntax, JSON schema agreement,
  fixture fields, Markdown relative links, citation IDs, immutable action
  references and YAML job shape. Query checks are **structural**, not a Kusto
  parser or live schema binding. Run KQL against the actual authorized
  workspace/Defender schema and connector before deploying analytic rules.
- Never upload SQLite spool, raw JSONL, tokens, actual prompts or verbose HTTP
  payloads as CI artifacts. `.gitignore` is a convenience, not a DLP control.
