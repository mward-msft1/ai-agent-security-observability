# Agent Framework, Agent 365 SDK/CLI and the two Microsoft OTel distributions

Sources [S1-S6,P1-P6,F1] in [the catalog](sources.md). Exact direct pins are in
[requirements-sdk.txt](../requirements-sdk.txt); all resolved validation
dependencies are in [requirements-sdk.lock](../requirements-sdk.lock).
Run from the root with an isolated environment, never by running another
private repository's deployment scripts.

## Product distinctions and migration

| Component | Purpose | It does not imply |
|---|---|---|
| Microsoft **Agent Framework** | Build/run/orchestrate agent code; instrument calls | Automatic Purview compliance ingestion or complete backend audit |
| Microsoft **365 Agents SDK** | Conversational channels, state, message delivery | Same package as Agent 365 SDK |
| Microsoft **Agent 365 SDK** | Extend existing agents with identity, governed Work IQ tools and notifications | Builds/hosts the agent or selects its model |
| **Microsoft OpenTelemetry Distro** (`microsoft-opentelemetry`) | Unified instrumentation/export setup; Agent 365, Azure Monitor, Foundry/OTLP according to configuration | Installing it registers identity, consents permissions or turns on every Purview policy |
| **Azure Monitor OpenTelemetry distro** (`azure-monitor-opentelemetry`) | Application Insights traces/metrics/logs via `configure_azure_monitor` | Sends compliance audit records to Purview or captures all prompts by default |
| Purview runtime Graph APIs | Compute protection scope and submit/evaluate selected user content | Export existing analytics/content from all AI services |

**Current official Agent 365 guidance deprecates the Agent 365 Observability
SDK packages for new integrations** [S1,S5]. Use Microsoft OpenTelemetry
Distro, not
`microsoft-agents-a365-observability-*` copied from an older sample.
`microsoft-agents-a365-runtime` (verified published version 2.0.0) remains
relevant for runtime/identity capabilities; notifications/tooling are separate.
We do not install unneeded mail/tool permissions merely to create traces.
The [official Agent 365 samples](https://github.com/microsoft/Agent365-Samples)
are additional implementation references, but their SDK constraints and
exporter providers are not this repository's tested lock. Their current S2S
guide specifies `/observabilityService/.../otlp/...`; do not copy older
non-`/otlp` route examples [S7].

## 1. Restore and validate packages

```powershell
python -m venv .venv-sdk
.\.venv-sdk\Scripts\python.exe -m pip install -r requirements-sdk.lock -e .
.\.venv-sdk\Scripts\python.exe -m pip check
.\.venv-sdk\Scripts\python.exe -m unittest discover -s tests -v
```

The lock was resolved on Windows/Python 3.14; CI exercises a clean Windows
restore. Other OS/Python targets require their own tested lock/resolution,
especially native wheels. Locked and tested pins: Framework core
**1.22.0**, OpenAI integration **1.17.0**, Microsoft distro **1.5.0**, Azure
Monitor **1.8.11**, and Azure Identity **1.27.0**. The manifest and lock pin
Agent Framework core to **1.22.0**, the version available from the configured
package feed and used by the local SDK validation environment. Release package
versions do not make every associated service feature GA.

## 2. Microsoft distro: console-only manual instrumentation [S1,S2]

```powershell
.\.venv-sdk\Scripts\python.exe -m examples.microsoft_distro
.\.venv-sdk\Scripts\python.exe -m examples.microsoft_distro --record-synthetic-content
```

Default run emits a real `invoke_agent` span with synthetic IDs/session but no
prompt or answer text. The opt-in run records **fixed synthetic** messages,
not arbitrary command-line/customer input. This demonstrates
`use_microsoft_opentelemetry`, `BaggageBuilder`, `InvokeAgentScope`, and
`record_input_messages` / `record_output_messages`.

The example explicitly disables Azure Monitor and A365 network export by
default, rejects ambient OTLP endpoint variables, disables SDK statistics
egress, uses an explicit synthetic Resource rather than cloud metadata
discovery, and disables unused OpenAI Agents instrumentation. Offline SDK tests
forbid socket connections and assert that real invocation spans are produced.
This example initializes only Microsoft OpenTelemetry Distro. Its current
guidance supports configuring Azure Monitor and Agent 365 as destinations in
the same distro setup. Do not initialize the separate Azure Monitor distro
provider in the same process as this example; choose one provider setup to
avoid conflicts or duplicate spans. The separate Azure Monitor example below
is an alternative, not a second provider to add to this process.

To instrument tools, use documented `ExecuteToolScope` / `ToolCallDetails` in
the upstream guide [S1] around the **real tool boundary**, keeping tool
arguments/results off by default. Wrap model inference separately when your
framework doesn't instrument it. A generic invocation span cannot infer files
actually read, response size, tool authorization or policy decisions.

## 3. Agent 365 export: pick the correct authentication scenario [S2]

All scenarios require tenant/agent identity baggage; missing baggage or token
resolver can lead to dropped/skipped spans in the SDK. Verify export outcome
and downstream record presence, not merely process exit.

| Scenario | Token / route | Key restriction |
|---|---|---|
| Standard custom-engine app, delegated OBO | Observability-scoped delegated token, `/observability` route | Explicit delegated `Agent365.Observability.OtelWrite` consent; Bot OAuth scopes must target observability |
| Standard custom-engine app, app-only S2S | Observability app-role token, `/observabilityService/tenants/{tenant}/otlp/agents/{agent}/traces` | Standard app needs `Agent365.Observability.OtelWrite` application permission/admin consent; agent route ID = ServiceConnection ClientId |
| Blueprint/registered Agent ID using OBO | Agentic delegated acquisition/cache, delegated `/observability` route | CLI setup doesn't necessarily configure delegated observability permission |
| Blueprint/registered Agent ID instance using S2S | Agentic identity token chain, `/observabilityService/tenants/{tenant}/otlp/agents/{agent}/traces` | **Not plain client credentials.** Microsoft Learn documents that registered blueprint instances don't need the Observability permission/admin consent; standard/unregistered apps still need the app role [S2,S7] |

The runtime example's `--agent365` mode demonstrates **only standard-app S2S**
with a pre-acquired observability token:

```powershell
# Supply these via your approved environment/secret mechanism, never commit them.
# A365_AGENT_ID must be the standard service connection's client ID for this mode.
.\.venv-sdk\Scripts\python.exe -m examples.microsoft_distro --agent365
```

Required values: `A365_TENANT_ID`, `A365_AGENT_ID`,
`A365_OBSERVABILITY_TOKEN` for resource
`api://9b975845-388f-4429-889e-eab1ef63949c`.
For this example's **standard custom-engine S2S** scenario, `A365_AGENT_ID`
must match the ServiceConnection client ID. The registered-agent-instance
sample path uses its deployed instance client ID, not its blueprint, service
principal object or agent-user ID [S2,S7].
The synchronous resolver receives cached credentials; this short demo does
not implement refresh/agentic token exchange. For production acquire tokens in
the approved auth layer, key the cache by tenant/agent/resource, refresh before
expiry and surface failed/skipped exports in health monitoring. Do not put
long-lived secrets or source Graph tokens in the resolver.

Do not assume an arbitrary OTLP exporter is an Agent 365 compliance
integration merely because its hostname matches a service. Prefer the pinned
Microsoft distro and documented authentication. No hand-written unverified
ingestion endpoint is used.

Agent 365 observability is an explicit product-integrated route; **Azure Monitor
or a generic OTLP collector alone doesn't write Purview compliance logs**.
Even for Agent 365 export, confirm the required service/policy/licensing and
actual compliance-view outcomes separately.

For code-level Purview enforcement within Agent Framework, use the
[Purview Developer Platform](https://learn.microsoft.com/en-us/purview/developer/)
and its [Agent Framework integration sample](https://github.com/microsoft/agent-framework/tree/main/python/samples/05-end-to-end/purview_agent)
as an additional current reference [P13]. It complements, but does not replace,
the runtime API and policy boundaries described above.

## 4. Agent Framework + Azure Monitor [S3,S4]

[framework_agent.py](../examples/framework_agent.py) uses the verified
`OpenAIChatClient(model=..., azure_endpoint=..., credential=...)` and
`as_agent(...).run(...)` APIs. Older `AzureOpenAIChatClient` examples may not
match this package generation.

1. Configure an Azure OpenAI model deployment and appropriate **Cognitive
   Services OpenAI User** runtime access (or equivalent documented model role).
   The example uses an intentionally approved `AzureCliCredential`, not
   interactive auth fallback.
2. Configure a workspace-based Application Insights resource and supply
   `APPLICATIONINSIGHTS_CONNECTION_STRING`, `AZURE_OPENAI_ENDPOINT`,
   `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`. Restrict backend access/retention.
3. Run only after approving model charges and telemetry egress:

```powershell
.\.venv-sdk\Scripts\python.exe -m examples.framework_agent --live
```

4. `--record-synthetic-content` calls `enable_sensitive_telemetry()`. Only the
   fixed synthetic request is used here, but the model output still leaves
   the model service and enters the selected trace destination. No raw
   response is printed in the default path.
5. Inspect trace IDs, spans and failure handling in Application Insights.
   Confirm sensitive attributes absent in the default path, and review
   instrumentor behavior on headers, exceptions and tools independently.
   [Azure Monitor KQL](../queries/sentinel/azure-monitor-traces.kql) uses
   workspace tables; classic Application Insights table names differ.

For Foundry-hosted/connected agents use the current project/service tracing
guide [F1]. Client traces and service traces need supported propagation and
project configuration; a client demo is not proof every service/tool call was
captured. Supported non-Microsoft frameworks can use distro auto-instrumentation
or manual scopes, regardless of AWS/GCP/on-prem hosting.

## 5. Purview: submit/evaluate both sides, don't confuse it with tracing [P1-P6]

```powershell
$env:CONTENT_CAPTURE_APPROVED = "true"
# ACCESS_TOKEN must be the approved Graph token for this user/app context.
.\.venv-sdk\Scripts\python.exe -m examples.purview_probe --live --user USER_OBJECT_ID --app POLICY_APP_CLIENT_ID
Remove-Item Env:\CONTENT_CAPTURE_APPROVED
```

This sends fixed synthetic prompt/response text **only when applicable policy
evaluation requires content**. Otherwise it sends metadata-only content
activities. The probe is not a live model implementation: it never invokes a
model, tool, another agent, email or Teams delivery.

The reusable gate:

1. Computes scopes for known user + protected app + activity.
2. Parses applicable scopes and applies the stricter inline requirement.
3. Honors scope actions before sending; for inline mode waits for content
   evaluation, errors on missing verdict/errors/unknown actions.
4. Sends current scope ETag in `If-None-Match`; recomputes when modified,
   bounded to avoid an endless policy-change loop.
5. Uses conversation `correlationId` and increasing `sequenceNumber`.
6. Treats 202/204 in offline mode as submission, **not an enforcement verdict**.

For a real app, wrap the input **before** model/tool execution and output
**before** delivery, integrating app authorization, runtime token refresh,
error UX, cancellation and approved retry/idempotency. Blocking only after
sensitive data already left for a model is too late. Some downstream M365
actions are governed by native workload policy rather than this generic text
probe. Follow the [Purview runbook](purview-policies.md) for what is actually
supported; don't infer response/file blocking from generic schema names.

## 6. Agent 365 CLI: pinned, privileged bootstrap separated from builds [S6]

The tool manifest pins **Microsoft.Agents.A365.DevTools.Cli 2.0.1** (.NET 8+):

```powershell
dotnet tool restore
dotnet a365 --version
dotnet a365 --help
dotnet a365 setup --help
dotnet a365 query-entra --help
```

Review current `setup requirements`, `setup blueprint`, `setup permissions`,
`query-entra blueprint-scopes`, `query-entra inheritance` and
`query-entra instance-scopes` help for the approved configuration/identifiers.
The published minimum setup roles differ by operation; OAuth2 grants can need
a separate administrator. The Microsoft-managed CLI enterprise app has a
documented client ID; its tenant service principal object ID is different.
Don't modify Microsoft's application to work around missing permissions.

**Do not run `a365 setup all`, `cleanup`, tenant-wide consent or policy creation
in ordinary build CI.** These can provision/modify/delete live resources and
some flows are interactive. Use one-time approved bootstrap followed by
separately authenticated environment-scoped deployment and read-only smoke tests.
The tool is version-pinned here but no tenant setup/deployment is claimed run.
Some installations use global `a365`; manifest execution avoids silently
using an unrelated global version.

## Content safety and egress checklist

Approve content fields/destinations and legal basis; minimize at source;
redact identifiers/resource URLs before generic trace export; avoid tool
secrets/headers; restrict all viewers; configure retention, hold and deletion;
disable console logging in production; test synthetic canaries for absence in
default mode. Regex redaction alone cannot ensure complete sanitization.
For policy evaluation, indiscriminately redacting text before classification
can destroy detection: send only authorized necessary content to Purview,
and apply separate minimization to ordinary operational telemetry.
