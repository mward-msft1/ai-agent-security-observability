# Microsoft 365 policy recipes: DLP, CC and IRM

Use this guide after the [customer overview](customer-guide.md) and
[Entra group/agent CA setup](entra-policies.md). These are **manual,
change-controlled instructions**, not commands that this repository runs.
Microsoft 365 Copilot policy locations do not automatically cover Copilot
Studio, Foundry or custom agents. Those require their supported data connections,
collection policies and, where applicable, runtime integration.

Evidence: [P8-P12](sources.md), retrieved 2026-10-29 UTC (2026-10-28 US Central).
Check your tenant's rollout, service-plan entitlements and portal labels.
Prompt blocking, agent risk and agent-specific IRM include preview features.

## Plan the controls and their subjects

| Policy | Pilot subject/location | Intended outcome | Not implied |
|---|---|---|---|
| Entra high-agent-risk CA | Explicit agent identities/blueprints/attributes under Agents | Block high-risk identity access to selected Entra-protected resources | Group-based agent-user CA, or a prompt-content inspection |
| Copilot DLP | Approved **human prompt submitters**; Microsoft 365 Copilot and Copilot Chat location | Restrict supported prompt processing, web search or labeled grounding content | All custom tools, uploaded-file inspection or every AI workload |
| CC Copilot interactions | Selected human users or supported mail-enabled scope; Copilot location | Route classifier matches to authorized human reviewers | Inline blocking or automatic guilt/intent determination |
| IRM Risky AI usage | Selected human users/groups and enabled indicators | Correlate supported risky user AI activity | Autonomous-agent identity risk or arbitrary service-principal group scope |
| IRM Risky Agents (preview) | Supported connected agents; service-provided default policy | Surface supported risky prompts, sensitive outputs/access and risky-site activity | Every agent type, immediate CA enforcement or arbitrary group scoping |

### Readiness and role separation

1. Confirm Microsoft 365 Copilot licensing for the relevant experiences and
   the applicable **DLP, CC and IRM** entitlements. Don't assume one Entra
   P1/P2 or Copilot license includes every Purview feature. Check each
   solution's linked licensing guidance [P8-P11].
2. Verify Purview auditing is on using the [existing audit steps](purview-policies.md).
   Confirm the pilot's actual supported records/collection before creating
   detections that depend on content.
3. Assign policy administration separately from content investigation.
   Use an appropriate least-privileged DLP role (for example the documented
   Purview Information Protection Admin role group); use **Communication
   Compliance Admins** for CC setup and the designated **Insider Risk
   Management Admins** for IRM. Give reviewer/analyst/investigator access only
   to the people who need it under each solution's role model.
4. Approve privacy notice, monitoring purpose, pseudonymization, retention,
   escalation and access review. Keep policy authors separate from routine
   reviewers where possible; group ownership alone grants no content access.
5. For **non-M365 AI data**, CC guidance requires configured Purview
   pay-as-you-go billing, even for some Microsoft services such as Copilot
   Studio. M365 Copilot data has no corresponding CC PAYG requirement [P9].
   Other solutions/indicators have their own billing and collection prerequisites.

## 1. Prepare the human and reviewer scopes

Use `SG-AI-Human-Users-Pilot` from the Entra runbook for policies that support
that user group. Do **not** substitute `SG-AI-Agent-Identities-Pilot`: its
service principals are not human prompt submitters or reviewable mailboxes.

For CC, an ordinary non-mail-enabled security group is not one of the
documented supported scoped-user group types. Choose explicit pilot users
or create a separate **distribution group**, as Microsoft recommends [P9,P12]:

1. An authorized Exchange recipient administrator opens
   `https://admin.exchange.microsoft.com` > **Recipients > Groups >
   Distribution list > Add a group**.
2. Choose **Distribution**. Name it `DG-AI-CC-Human-Users-Pilot`, enter the
   approved alias/email domain, and assign an accountable owner.
3. Add the approved **human mailbox users** matching the pilot roster. Keep
   direct, static membership; no nested or dynamic distribution groups.
   Set joining/leaving restrictions so owners control the compliance scope.
4. Review and create. Verify **Members** in the group's properties after
   replication. Reconcile this roster with the security-group roster through
   an approved change process; there is no automatic synchronization here.
5. Alternatively, use an existing **mail-enabled security group** if
   appropriate and supported. Do not treat a Microsoft 365 group as equivalent:
   CC documentation distinguishes communications sent to that group from
   each member's individual communications.
6. Designate **individual** CC reviewers with Exchange Online mailboxes and
   required CC permissions. CC reviewer assignment does not support groups;
   a group used to manage solution RBAC is a different mechanism.

## 2. Create Microsoft 365 Copilot DLP policies [P8]

Prepare approved synthetic positive/negative data and an existing sensitivity
label. Don't test with actual customer records. The user submitting the prompt
is the policy scope; the owner of the file being read is not the scope.

### Create the policy and scope

1. Sign in to `https://purview.microsoft.com` with authorized DLP policy access.
   Open **Solutions > Data Loss Prevention > Policies > Create policy**.
2. Choose **Custom > Custom policy**. Name it
   `DLP-AI-Pilot-Copilot-Data-Protection` and describe the intended controls.
3. If the **Admin units** step is available, choose the approved units or
   **Full directory** as appropriate. Administrative-unit support is rolling
   out; it governs management/eligible user scope, not agent identity groups.
4. Turn on **Microsoft 365 Copilot and Copilot Chat** as the location. Other
   locations are disabled for this policy; create separate policies for
   Exchange/SharePoint/endpoint controls when needed.
5. In that location's include/exclude settings select the approved human
   pilot users/group where supported by your tenant's picker. Verify actual
   membership and administrative-unit boundaries. If the group cannot be
   selected, use explicit users or the supported scope; do not broaden to
   all users just to complete the wizard.
6. Configure separate rules below, then select **simulation mode** initially.
   Save/review the policy, inspect simulation results and confirm the intended
   identities before turning on enforcement. Simulation does not block users.

### Rule A: keep sensitive prompt text out of external web search

1. Add `AI-Pilot-Restrict-Sensitive-Web-Search`.
2. Condition: **Content contains > Sensitive information types**. Select
   approved built-in or custom SITs and reviewed detection thresholds.
3. Action: **Prevent Copilot from processing content > Performing Web Searches**.
4. Configure supported alerts/notifications and policy tips appropriate to
   the pilot; route alerts to the operations team.
5. After approved activation, a matching synthetic prompt should not use
   external web search. **Copilot can still answer using permitted internal
   sources**; this is not full prompt blocking.

### Rule B: block processing of sensitive prompts (preview)

1. Confirm this preview has reached the tenant and intended Copilot experience.
2. Add `AI-Pilot-Block-Sensitive-Prompts` with **Content contains > Sensitive
   information types** and the approved SITs.
3. Action: **Prevent/Restrict Copilot from processing content > Processing
   prompts** (wording can vary). It prevents a response and use of that
   sensitive prompt for internal or external search.
4. After simulation/review and activation, validate a synthetic SIT match
   and a benign prompt. Check the user outcome and policy evidence, not just
   a generic refusal from the model. In-app preview messaging can be unclear.

### Rule C: exclude labeled files/emails from grounding

1. Add `AI-Pilot-Exclude-Restricted-Grounding`.
2. Condition: **Content contains > Sensitivity labels**. Select the approved
   labels, for example your organization's highly confidential label.
3. Action: **Prevent Copilot from processing content**.
4. Test with an authorized synthetic labeled file and an unlabeled control.
   The restricted item can still appear in citations even though its content
   is not used. Reopen Office files when testing label changes; the policy
   is evaluated at file open.

Do not combine SIT and sensitivity-label conditions in one rule. Use separate
rules/policies to isolate test outcomes. Policy updates can take **up to four
hours** to reflect. Native Copilot DLP does not scan files uploaded directly
into prompts; typed prompt text and supported labeled grounding items have
different coverage. Supported labeled-email coverage excludes calendar invites
and has the documented email-date limits. External-email grounding blocking is
a separate preview control; it is not content-based injection detection.

**Rollback:** authorized DLP admin returns the named policy to simulation/off
as supported, records the previous state and validates after propagation.
Do not remove labels, delete evidence or change unrelated data policies.
For Entra-registered **custom apps**, use the separate
[PowerShell/runtime policy recipe](purview-policies.md), not these M365 rules.

## 3. Create a Communication Compliance Copilot review policy [P9]

1. Verify CC roles, audit, licensing, content availability and the scope/
   reviewer setup above. Choose approved reviewers individually, not a
   distribution group as a reviewer.
2. In Purview open **Solutions > Communication Compliance > Policies >
   Create policy**. Choose the **Copilot interactions** template
   (**Detect Microsoft 365 Copilot and Microsoft 365 Copilot Chat interactions**),
   or the corresponding custom policy if your tenant exposes that workflow.
3. Name it `CC-AI-Pilot-Copilot-Interactions`. Choose the specific human
   users or the supported distribution/mail-enabled security group, with
   reviewed exclusions. Check any recommendation/insight option for
   out-of-scope users against the pilot privacy approval.
4. Verify the location is **Microsoft 365 Copilot and Microsoft 365 Copilot
   Chat**, not simply Teams/email. Retain the template's relevant
   inbound/outbound/internal directions and review the actual settings.
5. Review the template's **Prompt Shields** and **Protected material**
   classifiers; select only supported classifiers/conditions appropriate
   to the approved use case. A match flags potential risk, not a verdict on
   malicious intent or every kind of prompt injection.
6. Set the **review percentage** explicitly (100% of matching items is useful
   for a small pilot), assign the authorized individual reviewers, review
   the full configuration and create the policy. This is post-interaction
   monitoring, **not DLP simulation or an inline block**.
7. Generate an approved synthetic classifier test and benign control.
   Wait for supported processing/propagation and inspect policy status,
   alerts, matched classifier and authorized review view. The Copilot body
   evaluation interval is documented as one hour; this is not an end-to-end
   alert delivery SLA. Verify what content is actually available.
8. Document triage, false-positive labeling, escalation and privacy-safe
   evidence handling. Do not assume a remediation action supported for a
   Teams message also removes a Copilot interaction.

**Rollback:** stop/pause the named policy through the supported policy controls
after approval; preserve required alerts/cases and review access. Deletion or
scope changes are not a guarantee of erasing previously collected content.

For third-party/other Microsoft AI apps, configure the documented connected
AI collection and CC billing first. Their availability in a tenant's location
picker is not proof of content arriving. Never substitute the agent inventory
group for the policy's supported communication/user scope.

## 4. Configure IRM for human risky AI usage [P10]

1. Confirm IRM solution licensing, Admin/Analyst/Investigator roles, audit
   prerequisites and approved privacy settings. Keep pseudonymization on;
   identify who may reveal identities for authorized investigations.
2. In **Insider Risk Management > Settings > Policy indicators**, review and
   enable the supported indicators needed by the pilot. Some require
   additional billing, connections or signals.
3. For **Risky AI usage**, review the template's browser prerequisites:
   the Microsoft Insider Risk extension for Edge or Microsoft Purview
   extension for Chrome and at least one selected browsing indicator.
   Deploy/configure through your approved endpoint process. Don't claim a
   browser indicator covers a server-side/API-only agent.
4. Under **Insider Risk Management > Policies > Create policy**, select
   **Risky AI usage** and name it `IRM-AI-Pilot-Human-Usage`.
5. Choose **specific users and groups**, then select the approved human pilot
   scope. Review actual resolved membership; this is not service-principal
   monitoring. Use supported priority-content settings for approved sensitive
   information types, labels and data locations as applicable.
   IRM supports security groups, but **non-mail-enabled security groups cannot
   be selected when the policy is scoped to administrative units**. In that
   case select eligible explicit users or a supported mail-enabled group
   within the approved unit; do not broaden monitoring to work around the
   restriction. Guest accounts aren't supported in this user-policy scope.
6. Review the template's **built-in triggering events**, selected indicators,
   scoring window and thresholds. Start with documented defaults and a narrow
   scope. Do not assume every template has the Data leaks template's
   customizable DLP trigger selector.
7. If using generative-AI classifier indicators, complete the documented CC
   integration/data prerequisites; selecting an indicator alone doesn't
   create missing source content.
8. Finish/review the policy and check **Policies > Status** for missing
   indicators, users or prerequisites. Generate approved synthetic activity
   and inspect the resulting user timeline/alerts when scoring thresholds
   are met. A single event may not produce an alert.

IRM risk scoring is observation/investigation, not a real-time content block.
Adaptive Protection, if separately configured, is another policy integration,
not an automatic consequence of creating this policy.

**Rollback:** remove the pilot scope/stop scoring through the supported IRM
workflow after approval. Review case/retention consequences before policy
deletion; deletion can be irreversible and is not the default rollback.

## 5. Verify the separate Risky Agents policy (preview) [P11]

1. Complete IRM setup and supported licensing. Open **Insider Risk Management
   > Policies** and locate **Risky Agents (preview)**.
2. Current Microsoft documentation says this default policy is automatically
   present when the service is set up for supported licenses. **Inspect its
   existing coverage before assuming the pilot group limits it.** Do not
   create a duplicate or claim it is disabled by default.
3. Verify the agent types and required signal connections. The published
   supported types are **Copilot Studio agents, Microsoft Foundry agents and
   agents built using the P4AI SDK**. The SDK label here follows that page;
   merely installing Agent Framework or an OTel exporter is not equivalent.
4. Review observed risky prompts, sensitive responses, sensitive data access
   and risky-site indicators. Use supported synthetic tests, then inspect
   agent-related alerts through IRM's standard investigation workflow.
5. If default coverage doesn't meet requirements, follow the current custom
   IRM policy workflow and only the scopes/options actually exposed for that
   agent scenario. Microsoft does not document arbitrary agent security-group
   scoping for this default policy; do not promise it.
6. Ensure the investigator has the necessary unscoped access: **administrative
   units are not currently supported for agent alerts**, so a scoped analyst
   cannot see them. Guest-user interactions show sensitive-information
   indicators rather than full prompt/response content.
7. Record the approved monitoring scope and response owner. IRM agent risk
   is shared with documented DSPM/M365 admin experiences; it is **not the
   Entra ID Protection Agent risk condition**. No automatic IRM-to-agent-CA
   block is asserted here.

**Rollback:** have the authorized IRM admin review available controls for the
specific default/custom policy and signal integration; don't assume deleting
it, removing a directory-group member or toggling CA stops retained IRM data.

## 6. Record evidence before expanding scope

For each recipe record policy ID/version, owner, subject and resolved members,
location/resources, enabled mode, licensing/preview prerequisites, synthetic
test time, actual outcome and rollback result. Record **no raw prompts or
personal data** in ordinary change tickets. Check that the in-scope pilot is
affected and an out-of-scope control is unaffected by this policy (other
tenant-wide policies may still apply).

Only expand after identity/data owners approve results. Keep human access
risk, agent identity risk, data-policy matches, compliance review and insider
risk distinct in investigations and SIEM dashboards.
