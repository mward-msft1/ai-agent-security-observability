# Entra agent identity and access policy runbook

**Manual pilot runbook, not automatic tenant mutation.** Sources [E4,E6,E7,E9,E10,E11,E12,E13,S2,S5,S6]
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

### 2a. Strengthen human administrator sign-in with passkeys [E14]

Passkeys protect **human user authentication**; they don't authenticate an
autonomous app-only agent or replace agent-identity Conditional Access.
Microsoft Entra FIDO2 passkeys are available without an additional Entra
license. Conditional Access itself has separate licensing requirements.

1. As an Authentication Policy Administrator, go to **Entra ID > Security >
   Authentication methods > Policies > Passkey (FIDO2)**.
2. Before opting in to passkey profiles, review the irreversible change:
   opting in transfers global settings to a Default profile and Microsoft
   currently documents that profile opt-in **can't be undone**.
3. Create and assign a narrowly scoped profile to the approved human
   administrator/operator security group. Choose allowed device-bound or
   synced passkeys and any verified authenticator AAGUID restrictions.
   Synced passkeys don't support attestation; without attestation Entra can't
   guarantee a passkey's asserted type or other attributes.
4. If the requirement is to require phishing-resistant sign-in to sensitive
   resources, create a separate Conditional Access policy for the human users
   and require an appropriate built-in/custom authentication strength that
   allows the approved FIDO2 passkey. Keep approved emergency-access accounts
   excluded and test recovery before enforcement.
5. Test registration and sign-in on each supported platform with the pilot
   users. Attestation is checked at registration; enabling it later does not
   retroactively block already registered non-attested passkeys. Changing
   AAGUID restrictions can prevent existing users from signing in, so review
   the impact before updating an allow-list.

Passkey-profile group targeting is an authentication-method configuration for
**people**. It does not create an agent group scope or cause a passkey
requirement to apply to noninteractive agent credentials.

### 2b. Optional cross-language identity sidecar [E15]

For containerized polyglot applications, the Microsoft Entra ID Auth SDK
sidecar can centralize token acquisition/validation and downstream API calls.
It is a separate authentication architecture, not an audit collector, agent
registry, or requirement for this repository's examples.

The sidecar API must remain inside a trusted boundary (localhost/pod-local by
default); **never expose it publicly**. Every app within that boundary can
reach it, so admit only trusted, secured callers. Token validation is not
authorization: the application must still validate scopes/roles and authorize
the requested operation. See the [official sidecar security guidance](https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/security)
before deployment.

Microsoft Entra PowerShell is the current scenario-focused module built on
the Microsoft Graph PowerShell SDK [E16]. The group examples here use the
documented portal and Graph request; this reference does not silently depend
on the retired AzureAD module or imply a tested PowerShell automation script.

## 3. Select the correct Conditional Access target [E9]

| Actual access pattern | Correct target | Important limit |
|---|---|---|
| Agent accesses resource on behalf of signed-in human | That **human user** in delegated/OBO flow | Targeting agent identity alone does not cover this token |
| Autonomous app-only **Agent ID** access | Agent identity/blueprint via supported **Agents** targeting | Agent identity policy doesn't protect its separate agent user |
| Agent uses its **agent user account** | **Agent Users** assignment | Current docs explicitly say ordinary "Users" assignments/groups don't cover agent users |
| Traditional non-Agent-ID service principal | Supported workload identity targeting | Workload ID licensing and supported conditions differ; no MFA to a headless service principal |
| API key / non-Entra resource | No Entra CA token issuance boundary | Use platform/network/application authorization; CA cannot inspect/block that key use |

Base agent CA currently documents Microsoft 365 E7 or Agent 365 plus at least
Entra P1/M365 E3. **Agent risk-based CA additionally requires Entra P2/M365 E5
with Agent 365, or the documented Microsoft 365 E7 entitlement** [E11].
Agent risk and agent-user targeting are preview capabilities. Device-compliance conditions for agent users are limited to
documented execution-environment support (some conditions are preview).
Don't add human MFA controls to an app-only flow and expect them to succeed.

## 3a. Create security groups without confusing inventory with enforcement

**The requested group-scoped risky-agent CA pattern is not supported as an
ordinary user/group assignment.** Agent identities use **Agents** targeting;
Microsoft explicitly excludes agent-user group-membership scoping [E9,E11].
Create the groups below for their stated purposes, then configure the supported
agent CA assignments in section 4. Adding an agent to a group is not evidence
that a CA policy applies.

| Suggested scope | Members / purpose | Not a substitute for |
|---|---|---|
| `SG-AI-Agent-Identities-Pilot` | Approved agent service-principal objects; inventory and separately authorized resource access | Agents-targeted CA assignment |
| `SG-AI-Agent-Users-Pilot` | Optional linked agent user accounts; inventory and supported resource assignments | Agent Users CA targeting; ordinary Users policies don't apply |
| `SG-AI-Human-Users-Pilot` | Licensed human users who prompt Copilot/agents; supported human-user CA, DLP/IRM scopes | Agent identity/agent-user protection |
| `DG-AI-CC-Human-Users-Pilot` | Separate distribution group with the approved human pilot users | A non-mail-enabled security group or service-principal scope for CC |

### Create the security groups in Entra [E12]

1. Sign in to `https://entra.microsoft.com` as Groups Administrator (or an
   authorized equivalent). Go to **Entra ID > Groups > All groups > New group**.
2. Set **Group type = Security**, use the appropriate name above and enter
   a description naming its purpose, owner and change-review process.
3. Set **Membership type = Assigned**. Keep **Microsoft Entra roles can be
   assigned to the group = No**; this is not a role-assignable admin group.
   Do not assign access/roles to an inventory group as a side effect.
4. Add accountable human owners. For the human pilot group add the approved
   licensed human user accounts. For the optional agent-user group add only
   actual linked agent user accounts, not similarly named human accounts.
5. Create the group and record its **object ID**. Agent application client IDs,
   service principal object IDs and agent user object IDs are different values.
6. For the agent-identity group, add the approved **service principal object**
   using the authorized Graph membership operation below when the portal
   picker does not expose it. Don't replace it with its sponsor/owner.
7. Review direct members and map each object ID to the agent inventory.
   Review scope changes before broadening any policy. Avoid nested/dynamic
   membership in the pilot so effective membership is straightforward.

### Add an agent service principal when the portal picker cannot [E13]

Microsoft Graph supports service principals as members of a **security**
group, not a Microsoft 365 group. An authorized administrator can submit this
request using an already approved Graph client:

```http
POST https://graph.microsoft.com/v1.0/groups/{SECURITY_GROUP_OBJECT_ID}/members/$ref
Content-Type: application/json

{
  "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{AGENT_SERVICE_PRINCIPAL_OBJECT_ID}"
}
```

Supply a Graph-scoped bearer token via the client's protected authentication
mechanism, never in a ticket or committed file. Successful addition returns
204. The published permission table for adding a service principal requires
**GroupMember.ReadWrite.All AND Application.ReadWrite.All** for delegated or
application access; delegated callers also need the supported owner/directory
role. This is a privileged **administration** operation, not a new collector
permission. Do not consent these write permissions merely to run a read-only
query. Respect any additional Agent ID management restrictions; if the object
is rejected, stop and investigate rather than use a broader permission or
different object type as a workaround.

Verify the intended object appears in group membership through your approved
directory-management tooling; don't equate 204 with CA coverage. Remove only
the membership association through the approved group UI/process on rollback;
do not delete the identity. No membership or group is created by repository code.

### Scope the actual CA policy to the same approved set [E9,E11]

Use the inventory to select explicit **agent identity object IDs** in the
**Agents** assignment. For a stable class of agents use its **blueprint**;
that also covers future instances and can be broader than the inventory group.
At scale, use **custom security attributes** with the documented Agents
attribute picker and separately authorized attribute administration. Do not
enter a group object ID into an agent-ID field or invent a group filter.

Group changes do **not** synchronize CA selections or attributes automatically.
Keep an approved mapping/change checklist and compare the actual agent CA
assignment after onboarding/removal. For an agent's user account create a
separate **Select agent users (Preview)** policy and select those user objects
explicitly (or use supported attributes). Test each token subject separately.

For **human** delegated/OBO users, a regular user-risk/sign-in-risk CA policy
can target `SG-AI-Human-Users-Pilot` under **Users > Select users and groups**.
Use Entra ID Protection's licensed human-user risk guidance, Report-only and
the organization's emergency-access exclusions. Its risk condition is **User
risk / Sign-in risk**, not **Agent risk**, and it does not protect app-only
agent requests.

## 4. Pilot policy: high agent risk block

1. Sign in as Conditional Access Administrator with the required license.
2. Open **Protection > Conditional Access > Policies** (labels may change).
   Use the official **high-risk agent** template or create a named pilot
   policy following *Secure autonomous agents* [E9].
3. Name the policy `CA-AI-Pilot-Block-High-Agent-Risk`. Under
   **Assignments > Users, agents or workload identities**, set **What does
   this policy apply to? = Agents**. Include **Select agent identities** and
   explicitly select the approved agent objects from section 3a, or a reviewed
   blueprint/attribute scope. Confirm the effective target isn't its agent
   user, signed-in human, or inventory security group.
4. Under **Target resources**, select intended Entra-protected pilot resources
   (Microsoft's broader baseline uses **All resources**). Under
   **Conditions > Agent risk (Preview)** set **Configure = Yes > High**.
   Under **Access controls > Grant**, choose **Block access > Select**.
5. Set **Enable policy = Report-only**, review the selected object IDs and
   resources, and choose **Create** [E11]. Record the policy ID/change owner.
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
supported endpoint/network restrictions for **agent user accounts**. For
agent identities the current condition is Agent risk and the grant control
is Block; don't add unsupported device/location controls [E11].
Treat each as a separate policy
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
