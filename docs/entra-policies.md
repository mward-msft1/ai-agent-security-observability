# Entra agent identity and access policy runbook

**Manual pilot runbook, not automatic tenant mutation.** Sources [E4,E6,E7,E9,E10,S2,S5,S6]
are listed in [the catalog](sources.md). Recheck tenant rollout/licensing.
Back up existing policy JSON, names/IDs, role assignments and owner approvals.
Use least privilege and emergency-access procedures; never test enforcement on
all identities first.

## 1. Inventory, registration and ownership

1. Inventory first-party agents through their native platform/Agent 365
   integration. For connected platforms, configure the platform's supported
   registry sync; verify what it actually brings (inventory vs runtime data).
2. For custom code, choose a **standard app registration** or **Agent ID
   blueprint/instance** according to the official integration path. Don't
   relabel an arbitrary service principal as an Agent ID.
3. Record owner/sponsor, business purpose, host/framework, model/tool data
   boundaries, tenant, client app ID, service principal object ID, blueprint
   and instance IDs, optional agent user ID, retention and incident contact.
4. Use the CLI's read-only queries after approved setup to verify permissions
   and inherited grants. Setup roles differ from runtime grants. Agent user
   accounts/mailboxes and notifications have Frontier preview prerequisites.
5. Disable/remove unused agents and grants through an approved lifecycle
   process; preserve investigation evidence according to retention.

## 2. Consent and least privilege

1. Create **separate identities** for read-only collection and destination
   ingestion. Use the [operation matrix](permissions.md), not a broad
   all-permissions registration.
2. Review requested tool/API scopes and delegated vs app-only mode. Prefer
   scoped resources (for example site-specific access when the tool supports
   it) and approved user contexts. Consent is not data ownership authorization.
3. Review tenant user-consent policy/admin-consent workflow and publisher
   verification requirements. Route privileged consent to authorized admins,
   not an unattended agent build.
4. Prefer managed identity/federated credentials/certificates where the
   target SDK/service supports them. Standard cloud federation is not a
   drop-in replacement for a documented Agent ID token chain.
5. Validate runtime `tid`, `aud`, `appid`/authorized party and token subject
   in the actual auth library/resource flow; don't log tokens or accept a
   token merely because its JWT payload looks right.

## 3. Select the correct Conditional Access target [E9]

| Actual access pattern | Correct target | Important limit |
|---|---|---|
| Agent accesses resource on behalf of signed-in human | That **human user** in delegated/OBO flow | Targeting agent identity alone does not cover this token |
| Autonomous app-only **Agent ID** access | Agent identity/blueprint via supported **Agents** targeting | Agent identity policy doesn't protect its separate agent user |
| Agent uses its **agent user account** | **Agent Users** assignment | Current docs explicitly say ordinary "Users" assignments/groups don't cover agent users |
| Traditional non-Agent-ID service principal | Supported workload identity targeting | Workload ID licensing and supported conditions differ; no MFA to a headless service principal |
| API key / non-Entra resource | No Entra CA token issuance boundary | Use platform/network/application authorization; CA cannot inspect/block that key use |

Agent CA currently documents Microsoft 365 E7 or Agent 365 plus at least
Entra P1/M365 E3. Device-compliance conditions for agent users are limited to
documented execution-environment support (some conditions are preview).
Don't add human MFA controls to an app-only flow and expect them to succeed.

## 4. Pilot policy: high agent risk block

1. Sign in as Conditional Access Administrator with the required license.
2. Open **Protection > Conditional Access > Policies** (labels may change).
   Use the official **high-risk agent** template or create a named pilot
   policy following *Secure autonomous agents* [E9].
3. Assign **Agents**, select only approved pilot agent identities or their
   pilot blueprint. Confirm the effective target isn't its agent user or
   signed-in human.
4. Select intended Entra-protected target resources and the supported
   **Agent risk = High** condition; use **Block access**.
5. Start **Report-only** where the selected policy/conditions support it.
   If a control doesn't support report-only, use an isolated nonproduction
   agent and approved test plan rather than silently enforcing.
6. Review report-only/sign-in evaluation against benign pilot access and a
   controlled authorized risk scenario. Do not simulate malicious tenant
   operations or mark an agent compromised without separate approval.
7. Confirm risky-agent reports and policy targeting. Agent detections are
   offline and have learning behavior; this is not a synchronous prompt
   injection/content filter. OBO risk is attributed to the human user.
8. Enable the narrowly scoped policy only after review. Confirm a fresh
   token request is blocked as expected; existing token lifetimes/CAE
   support affect timing.

Optional follow-ons: approved-agent custom-security-attribute targeting and
documented network/location restrictions. Treat each as a separate policy
with prerequisites, exclusions and evidence, not a universal control supported
by every agent flow.

## 5. Turn on evidence before enforcement

Enable the relevant Entra diagnostic categories [E7] and Microsoft Graph
activity logs [E10]. Use the native connector path in [SIEM guidance](siem.md).
Record app/service principal ID mappings. Run the
[sign-in](../queries/sentinel/agent-signin-details.kql) and
[Graph request](../queries/sentinel/graph-data-access.kql) queries. Confirm
policy evaluation outcomes and identity subject, not just HTTP status.

## 6. Rollback and incident response

1. Capture the policy ID, prior state, observed affected identities and
   validation time; don't put prompt content in the change ticket.
2. Disable/revert **only the named pilot policy** with an authorized
   administrator; verify token issuance behavior after the change.
3. Keep telemetry/reconciliation enabled. If compromise is confirmed use the
   documented risky-agent report actions/disable workflow and preserve data.
   Risk dismissal is a distinct action from removing a CA block.
4. Revoke unnecessary grants/credentials only through approved identity
   lifecycle response; don't rotate unrelated tenant credentials blindly.

### Enforcement boundaries

CA evaluates resource token issuance/refresh, not model reasoning. Agent
blueprint provisioning and intermediate token exchanges have documented CA
exceptions; the actual agent resource access is the protected boundary [E9].
Neither inventory, a sign-in, nor a risk report contains all prompt/response or
tool content. Non-Microsoft hosts can use Entra controls for Entra-protected
resources, but their other cloud APIs need their own controls and audit.
