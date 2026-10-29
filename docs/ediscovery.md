# Investigating AI interactions with Microsoft Purview eDiscovery

Use this runbook to **preserve, find, review and produce available AI evidence**
after a security incident, compliance escalation or authorized legal request.
It complements [DLP, CC and IRM](m365-policy-recipes.md), not replaces them.
Start from the [customer home page](../README.md) for the wider security workflow.

Official sources were retrieved **2026-10-29**. Source IDs [L1-L9] resolve in
[the catalog](sources.md); direct Microsoft procedure links are included below.
These are manual, change-controlled customer tasks. No case, hold, export,
deletion or tenant change is executed by this repository.

## What eDiscovery adds to your security toolkit

| Practitioner need | Correct task | Important boundary |
|---|---|---|
| An IRM/CC/Defender finding needs content review | Open an authorized case; search the relevant person's stored AI interactions | An alert, a policy match and proof of a violation are different things |
| Evidence could be deleted during investigation | Apply and verify a case hold on approved content locations | Hold configuration is not successful preservation until location status is verified |
| Determine what a user asked and what AI returned | Search supported mailbox AI item classes and review matching items | Audit metadata and Entra sign-ins are not substitutes for stored prompt/response content |
| Determine which business information was involved | Collect relevant files, versions, linked content and audit evidence separately | A prompt citation or file link doesn't preserve its target or prove all backend reads |
| Give approved reviewers a stable working set | Add responsive results to a review set with eligible premium features | A review set is a separate copy; the search is rerun during collection |
| Produce evidence to another authorized team | Export approved content plus reports; record custody and protect copies | This is an evidence workflow, not a continuous SIEM feed |
| Remediate an AI data spill | Use a separate approved search-and-delete process | Purge can conflict with preservation duties; no purge commands are supplied here |

## 1. Confirm where the evidence actually exists

Select the **human user's Exchange Online mailbox** for supported stored
prompt/response items, not the agent's inventory security group or a
service-principal display name. An autonomous agent without a supported
mailbox/collection path isn't made discoverable by registration alone.

Use the official [AI item-class catalog](https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data)
and verify representative pilot items before assuming coverage [L1,P5].

| Experience | Documented ItemClass / location | Prerequisite or gap |
|---|---|---|
| Microsoft 365 Copilot | `IPM.SkypeTeams.Message.Copilot.*` in user mailbox; BizChat uses `IPM.SkypeTeams.Message.Copilot.BizChat` | Covers stored supported interactions, not every AI runtime event |
| Copilot Studio | `IPM.SkypeTeams.Message.Copilot.Studio.*` in the supported user mailbox path | Verify experience, capture and actual items; this isn't the Dataverse transcript collector, and doesn't remove its recording/redaction limits |
| Microsoft Foundry | `IPM.SkypeTeams.Message.ConnectedAIApp.AzureAI.<AzureResourceName>` | Requires the supported capture configuration; Foundry/OTel tracing alone isn't this mailbox ingestion |
| Entra-registered custom AI app | `IPM.SkypeTeams.Message.ConnectedAIApp.Entra.<AppID>` | Purview integration, known-user context, actual content submission and a collection policy [P5] |
| Connected third-party AI app | `IPM.SkypeTeams.Message.ConnectedAIApp.Connector.<AppName>` or browser `IPM.SkypeTeams.Message.CloudAIApp.SaaS.<AppID>` | Supported connector/browser collection prerequisites; the class is not a promise of arbitrary SaaS access |
| Copilot Pages / Notebooks artifacts | `.page`/supported files in their actual SharePoint, OneDrive or user-owned SharePoint Embedded location | Collect the file/container separately from mailbox interactions [L8] |
| Copilot personalization / memory | `IPM.Contact` | Separate scope; deleting conversation items doesn't delete associated memory. Not every contact is an AI memory [L1] |

Angle-bracket values above are documented placeholders, not literal IDs or
wildcard syntax to paste unchanged. Verify the app/resource identifier from
real pilot metadata. Do not invent a class from an agent's friendly name.

For Entra apps, establish and test collection using the
[Purview integration runbook](purview-policies.md) before this workflow.
There is no retroactive recovery of prompts that were never collected.
Preserve independent [audit](api-surfaces.md), [identity](entra-policies.md)
and [SIEM](siem.md) evidence through their own retention/access processes.

## 2. Establish authority, roles, licenses and billing

1. Record the incident/request ID, legal/privacy authority, custodians, UTC
   time range, suspected app, purpose, permitted content and export recipients.
   Have counsel or the designated evidence authority approve preservation
   scope. Security access alone isn't permission to inspect all employee content.
2. Verify [eDiscovery setup and subscriptions](https://learn.microsoft.com/en-us/purview/edisc-get-started)
   and [billing](https://learn.microsoft.com/en-us/purview/edisc-billing) [L2,L7].
   The setup guide requires appropriate E3/E5 licensing for operators; premium
   review/analytics features need the eligible higher tier/add-on. Verify
   licenses of **users whose content is held**, not just the operator.
   The hold guide separately identifies premium query-based, time-bound and
   custodian-scoped capabilities; do not assume every hold option is in E3 [L4].
3. Assign [eDiscovery permissions](https://learn.microsoft.com/en-us/purview/edisc-permissions)
   through **Purview > Settings > Role groups** (navigation
   can vary). Use **eDiscovery Manager** for case operators and membership in
   the particular case. Reserve **eDiscovery Administrator** for tightly
   controlled cross-case oversight/recovery [L3].
4. For least-privilege separation, use approved role combinations for **Case
   Management**, **Compliance Search**, **Hold**, **Preview**, **Review** and
   **Export** as the task needs. Review-only access doesn't imply export.
   **RMS Decrypt** is separate and only for authorized supported decryption.
   Do not grant **Search And Purge** to routine investigators.
5. If assigning the eDiscovery Managers subgroup through group membership,
   Microsoft documents **mail-enabled security groups**, not Exchange
   distribution groups or Microsoft 365 groups. Administrators are individual
   users. These are investigator-access groups, not CC monitored-user groups,
   agent inventory groups or the data sources to preserve [L3].
6. Confirm required eDiscovery enterprise applications are enabled using
   the setup guide. Troubleshoot CA restrictions with the identity team;
   do not disable tenant security controls to make an export work.
7. Approve non-M365 AI pay-as-you-go billing before adding that content to
   review sets or exporting it. Microsoft-owned services such as Security
   Copilot can still be **non-M365 AI data** for billing. Search/hold/case
   management processes are distinct from chargeable collection/export storage.
   Closing a case doesn't eliminate retained non-M365 AI storage charges [L7].

See also the repository [permissions matrix](permissions.md). Purview Audit
Reader, Content Explorer roles and Graph audit scopes do not grant case access.

## 3. Create the case and document its scope

Follow [Create and manage cases](https://learn.microsoft.com/en-us/purview/edisc-cases-manage) [L2].

1. Open [Microsoft Purview](https://purview.microsoft.com) >
   **Solutions > eDiscovery > Cases > Create case**.
2. Use a unique name, for example `AI-Synthetic-Pilot-2026-10`, and describe the
   approved question, owner, UTC window and synthetic-only scope.
3. Under case settings, assign only approved members. Confirm an authorized
   recovery/oversight path if the creator leaves.
4. Select the approved mailboxes and site locations in the search/hold data
   source controls. Where licensed, add reusable case-level data sources.
   Keep a source manifest: user object ID/SMTP, site/container URL, app ID,
   reason included, expected evidence and scope approver.
5. Keep the Entra agent ID, blueprint ID and human mailbox identity separate.
   A Copilot application name in a result's From/To headers can identify the
   application participant; it isn't a routable mailbox to add as a source [L1].

## 4. Preserve before evidence disappears

Follow [Create holds](https://learn.microsoft.com/en-us/purview/edisc-hold-create)
and [Manage holds](https://learn.microsoft.com/en-us/purview/edisc-hold-manage) [L4].
Do this promptly after authority is established; don't wait for perfect queries.

1. In the case, select **Hold policies > Create policy**. Name it and record
   the preservation instruction.
2. Add the approved mailbox/site data sources. Prefer an explicitly reviewed
   list over an assumed group-wide scope.
3. Choose location-wide preservation or a legally approved query/date scope
   supported by the license. An AI-only keyword hold can miss relevant files,
   context and partially indexed content. Never copy a narrow search into a
   hold without reviewing its preservation consequences.
4. Select **Apply hold**, then review each location under **Details** for
   status/errors. A hold can take **up to 24 hours** to take effect. Record
   application time, resolved sources and successful status; investigate and
   retry failed locations rather than marking them protected.
5. Group membership for a hold is a **point-in-time snapshot**. New members
   aren't automatically held, and removed members remain held until updated.
   Search membership resolution differs. Reconcile approved source changes
   explicitly; an inventory/CA pilot group isn't continuous legal preservation.
6. Preserve linked SharePoint/OneDrive files and relevant versions separately.
   A mailbox hold doesn't implicitly hold every file referenced by its messages.

Creating a hold from a search does **not** copy that search's query into the
hold policy; inspect and explicitly configure the hold. Holds cannot recreate
content already gone, and are not a replacement for long-term retention policy.

## 5. Find the AI interactions and verify the search

Follow [Create a search](https://learn.microsoft.com/en-us/purview/edisc-search-query) [L5].

1. In **Cases > your case > Searches**, create a named search and select the
   approved user's mailbox as a source.
2. For a broad AI baseline, use **Add condition > Type > Contains any of >
   Edit > Copilot activity**. Current guidance also describes this as the
   **Item class / Copilot activity** choice. This includes supported Copilot
   and other AI application activity, not just one product [L1,P5].
3. Add a UTC date range. Start with the known synthetic marker
   `AI-EVIDENCE-PILOT-20261029` in prompt and response, then refine by the
   supported ItemClass values in section 1 for the app being investigated.
   Confirm the actual stored class in pilot results.
4. Generate **Statistics**; record estimates, responsive locations, failures
   and indexing limitations. Generate **Sample** results to inspect relevance.
   A sample is not a complete export or proof that all responsive items exist.
5. Save query text/conditions, source resolution, run time, process ID and
   reports. Compare the synthetic event against app submission, audit and
   available content evidence without assuming cross-service IDs are equal.
6. If content is absent, check the selected mailbox, date/time conversion,
   collection policy/integration, retention, role/case membership, indexing
   and job errors. Widen scope only with authority. No hits doesn't prove
   the agent never acted.

**Query-language warning:** eDiscovery content searches use **Keyword Query
Language (KeyQL)**. The Defender/Sentinel `.kql` files in this repository use
**Kusto Query Language** and cannot be pasted into this search. Optional
advanced review-set Kusto exploration is a different, preview feature [L2].

### Collect Copilot Pages separately when relevant

Follow [Use eDiscovery with Copilot Pages](https://learn.microsoft.com/en-us/microsoft-365/loop/copilot-pages-ediscovery?view=o365-worldwide) [L8].
Selecting a user's OneDrive alone does **not** include their Pages/Notebooks
in a user-owned SharePoint Embedded container.

1. An authorized **SharePoint Embedded Administrator** locates **SharePoint
   admin center > SharePoint Embedded > Active containers**.
2. Filter **Application name: Loop**, **Ownership type: User**, then locate
   the **Principal owner** and copy the container URL from **General**.
3. Add the supported container URL as a site data source when it isn't
   available in the picker. Include it in the approved search and hold.
   The URL identifies a data location; it doesn't grant browsing access.
4. Search the file content and relevant versions. The `.page` artifact and
   its link in a chat/email are different items. Record version selection.
   Supported HTML conversion can aid review with the appropriate license.

Container support is documented as **preview** in current case guidance;
group-owned/app-owned containers aren't currently supported there [L2].
Do not extrapolate user-owned container support to every embedded app.

## 6. Review a stable evidence set

With eligible premium features, follow
[Add search results to a review set](https://learn.microsoft.com/en-us/purview/edisc-search-add-to-review-set) [L6].

1. From the search select **Add to review set**, then choose a new or existing
   set. Record whether all results or an explicitly approved sample is collected.
2. Choose treatment of partially indexed items, cloud attachments, document
   versions and supported HTML conversion. Record these choices: they can
   expand collection beyond visible keyword hits.
3. Monitor **Process manager** until completion and resolve errors. The search
   runs again when results are added, so collected counts can differ from
   earlier estimates. Reconcile changes rather than silently dropping items.
4. Approved reviewers assess the content and apply case tags such as
   `Relevant`, `Needs legal review`, `Sensitive data` and `Not responsive`.
   Preserve prompt/response context where available. A classifier match isn't
   itself a legal conclusion or proof of exfiltration.
5. Treat the review set as a separate content copy. Access it through Purview
   and approved exports, not an assumed customer-accessible storage account.

## 7. Export only approved evidence and maintain custody

Use [search export](https://learn.microsoft.com/en-us/purview/edisc-search-export)
or [review-set export](https://learn.microsoft.com/en-us/purview/edisc-review-set-export) [L6].

1. Obtain export approval and verify the **Export** role. Choose a search
   export for responsive in-place results or an approved filtered/tagged
   review-set export. Capture the precise selection and expansion options.
   For a search, open it under **Searches** and select **Export**. For a review
   set, open **Review sets > your set > All items**, select the approved items
   or filter, then **Action > Export**.
2. Export item reports and the permitted content format. Review privacy,
   privilege, redaction and linked-item choices before release. In review-set
   exports, selecting redaction doesn't universally remove native conversation
   files; current guidance says conversations can include **both** native and
   redacted files. Inspect the package rather than assuming it is safe to share.
3. Check process status and error reports. Download every required package
   before expiry: **search exports: 14 days from creation**;
   **review-set exports: within 30 days after completion**. These aren't
   source-content retention periods.
4. Keep process/settings reports, counts, errors, operator identity, UTC
   timestamps and recipient approval with the evidence. As a recommended
   custody practice, calculate SHA-256 for downloaded packages, record transfer
   events and verify hashes after copying to approved encrypted evidence storage.
5. Restrict recipients and set destination retention separately. Don't upload
   raw prompts to a generic SIEM or place evidence in this Git repository.
   Purview source deletion does not delete downloaded copies.

## 8. Separate spill remediation from preservation and closure

The official [AI search-and-delete procedure](https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data)
requires **Search And Purge** and documents a limit of **10 items per mailbox
per action** [L1]. It is not a bulk purge or routine collection workflow.
Conversation deletion doesn't delete associated Copilot memory.

**Do not release holds or retention to make purge succeed without legal,
privacy and incident-response authorization.** The product procedure discusses
removing/reapplying holds for deletion; that can destroy preservation and is
not recommended here as an automatic response. Use a separately approved
remediation plan and verify all affected copies and retention obligations.

Closing or deleting an eDiscovery case turns off its holds [L2]. Obtain explicit
release authorization, verify downstream evidence retention and inspect
location status before closure. A closed case can still incur non-M365 AI
storage charges [L7]; cost reduction isn't authority to delete evidence.

## Optional automation: a supported roadmap, not a telemetry collector

The [Graph eDiscovery API v1.0 overview](https://learn.microsoft.com/en-us/graph/api/resources/security-ediscovery-apioverview?view=graph-rest-1.0)
documents cases, searches, holds, operations and review sets [L9].
Do not substitute these APIs for journaling, mass downloads or SIEM streaming.

E3/Standard supports delegated standard operations with documented pay-as-you-go
requirements; app-only and premium operations require E5/equivalent add-ons.
The billing page requires PAYG activation for E3 API use and currently meters
export volume, not all operations [L7,L9]. Verify the individual endpoint's
OAuth permissions, case authorization and license before implementation.
No new eDiscovery API permission is required for the repository's existing
collectors. This update adds portal procedures, not legal export automation.

## Synthetic customer acceptance checklist

| Check | Evidence to record |
|---|---|
| Authorized pilot source | License, source manifest, case ID and approved members |
| Known interaction found | Synthetic marker, app/UTC time, stored class, prompt/response coverage or documented gap |
| Relevant artifacts covered | Separate source/file/container and version list; no assumed linked-file preservation |
| Hold verified | Every approved location's final status; no unresolved failure described as protected |
| Collection reconciled | Search estimates vs actual review-set/export counts, indexing and error reports |
| Export protected | Approval, package inventory/hashes, access controls and expiry-aware download |
| Release controlled | Explicit hold-release/closure authority and retained evidence plan |

No live case, search, hold, content review, billing or export was exercised
while writing this runbook. Test each licensed experience using synthetic data
before using it in a real investigation.
