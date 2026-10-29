# Purview audit, collection and data policy runbook

**No policy is applied by the examples.** Use an isolated pilot, approved
synthetic positive/negative data and a change record. Sources [A1-A5,P1-P7]
resolve in [the source catalog](sources.md). Portal navigation can differ by
DSPM/classic rollout; use the current product guidance.

## 1. Establish scope, licenses and administrative separation

1. List target experiences separately: M365 Copilot, Copilot Studio, Foundry,
   Entra-registered custom AI apps, and unmanaged browser AI usage. A policy
   location for one doesn't automatically cover another.
2. Confirm subscriptions, per-feature licensing and **pay-as-you-go** for
   Entra-registered AI-app management [P5]. Document Azure billing owner and
   expected classification/retention cost.
3. Assign Audit Reader to investigators, solution-specific policy-management
   roles to admins, and content-viewing roles only to approved reviewers.
   **Content Explorer Content Viewer** is needed for documented prompt/response
   viewing in relevant activity explorer flows; policy admin access is not
   blanket content access. CC/IRM/eDiscovery have separate roles.
4. Record content notice/consent/legal basis, pseudonymization, reviewer
   segregation, export approval and destination access. Set retention before
   generating anything beyond synthetic data.

## 2. Verify audit, then baseline metadata

1. In Purview **Solutions > Audit**, confirm auditing is enabled. An authorized
   Exchange Online operator can inspect:

```powershell
# Run in an already authorized Exchange Online PowerShell session.
Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
```

2. If disabled, follow the official Audit enablement procedure with the
   appropriate **Audit Logs** role; don't have the collector change it.
3. Generate one synthetic interaction in each target experience, recording
   pilot user/app/time locally without real business data.
4. Search the narrow time/user/operation range. For Copilot use
   `CopilotInteraction`; custom integrated enterprise apps use
   `connectedAIAppInteraction` where configured [A2,P6].
5. Verify how/when/app host, available resource references and labels.
   Message IDs do **not** prove prompt text is in that record. Export via the
   bounded [Audit Search API example](quickstart.md) only after Graph consent.
6. Measure ingestion latency and repeat after the documented/observed delay;
   distinguish no records, denied permissions and disabled logging.

## 3. Enable custom AI-app interaction collection

1. Register the application and choose a known-user auth model. The protected
   **application location ID** used in Purview policy is not automatically
   interchangeable with an Agent ID object/blueprint ID.
2. Integrate compute/protection and content processing [P1-P4]. Merely
   registering the app, installing a package, or turning on Azure Monitor
   does not send its interactions to Purview.
3. In **DSPM for AI (classic) > Recommendations > Secure interactions from
   enterprise apps**, review/create **Capture interactions for enterprise AI
   apps** (or the corresponding current DSPM collection policy). Scope and
   authorize the pilot users/apps according to supported controls.
4. Verify the policy appears under **DSPM > Collection policies**, billing is
   configured, and the app sends its actual selected content/metadata.
5. Run the explicitly opt-in [synthetic probe](../examples/purview_probe.py).
   Verify audit event, Activity explorer, sensitive information classifications
   and the configured app location. Reports may take at least a day [P5].
6. Test **both** prompt (`uploadText`) and response (`downloadText`) paths,
   while acknowledging the documented custom-app DLP enforcement scope below.
   Don't conclude a response is blocked just because it was submitted.
7. Roll back by disabling only the pilot collection policy and app submission
   path. Preserve retained/held data; stopping future collection is not deletion.

If compute returns no applicable scopes, the reference submits metadata only.
That is not a promise of archived prompt text. A collection policy plus actual
content submission must be tested end to end for the desired compliance output.

## 4. Pilot DLP with the actual supported location/action [P2,P4,P5]

For Entra-registered AI apps, current official guidance says the portal does
**not** create the needed app-scoped DLP policy: use the Security & Compliance
PowerShell cmdlet. Current AI-app capability documentation specifically
describes **blocking prompts based on sensitive information types**, not
universal response/file/tool blocking.

1. Validate an existing sensitive information type using an approved synthetic
   positive sample and a negative control; never include actual credit cards,
   employee records or customer data.
2. Confirm the exact Entra protected-app client ID and pilot app ownership.
   Arrange the Data Loss Prevention policy-management role and authorized
   `Connect-IPPSSession` separately from read-only collector auth.
3. Adapt official `New-DlpComplianceRule` **Example 4** [P7]. The documented
   shape is shown here for review; do not paste into a production tenant:

```powershell
$pilotAppId = "REPLACE_WITH_APPROVED_PILOT_APP_ID"
$locations = @(
  @{
    Workload = "Applications"
    Location = $pilotAppId
    LocationDisplayName = "Approved synthetic pilot"
    LocationSource = "Entra"
    LocationType = "Individual"
    Inclusions = @(@{Type = "Tenant"; Identity = "All"})
  }
) | ConvertTo-Json -Depth 6 -Compress -AsArray

# These are administration commands; intentionally not run by repository code/CI.
# Official example uses Mode Enable: only use an isolated pilot app after approval.
New-DlpCompliancePolicy -Name "Synthetic agent pilot" -Mode Enable `
  -Locations $locations -EnforcementPlanes @("Application")
New-DlpComplianceRule -Name "Synthetic prompt SIT block" -Policy "Synthetic agent pilot" `
  -ContentContainsSensitiveInformation @{Name = "Credit Card Number"} `
  -RestrictAccess @(@{setting = "UploadText"; value = "Block"})
```

4. The example's tenant-wide inclusion is constrained to the **one pilot app**.
   Don't call it a pilot-user-only policy. Where supported, start simulation/
   test mode before enforcement; otherwise use the isolated app and explicit
   approval. Do not invent unsupported report-only settings for this API path.
5. Recompute scopes; `uploadText` should require `evaluateInline` for a blocking
   policy. If only offline scopes appear, verify the PowerShell-created
   app-scoped policy, app location and collection configuration.
6. Invoke synthetic positive/negative probes. The app must stop before the
   model/tool/other-agent call when `restrictAccess` is returned; after a
   generated response, evaluate before delivering it if applicable.
7. Verify a real policy action, not merely a local regex or trace warning.
   Test API failure, unknown action, changed ETag and 202/204 without inline
   verdict. These cases are explicitly handled by the fail-closed probe.
8. Roll back the named rule/policy through the authorized administrator;
   restore its documented prior mode or disable it. Revalidate scopes and
   a negative control; preserve event evidence and required records.

Native M365 Copilot DLP policies and Power Platform connector/data policies
are separate families. Review their documented supported locations/actions
rather than applying this custom-app command to all first-party agents.

## 5. Labels and underlying data access

1. Establish/publish the organization's sensitivity labels using Information
   Protection roles; enable supported SharePoint/OneDrive label processing
   and encryption rights as required by the official guidance [P5].
2. Test an authorized and an unauthorized synthetic file read through each
   agent's real resource access path. Label ID in an audit record is evidence
   of a reference, not proof of correct access enforcement.
3. For custom tools, enforce native service authorization and applicable
   encryption/rights; do not assume submitting a label string to a telemetry
   exporter enforces the label. Purview won't download a URL on the app's behalf.
4. Roll back only pilot label publication/policy changes; removing a label
   from existing protected data requires a separately approved data operation.

## 6. Optional IRM, communication compliance and eDiscovery

These are separate solutions with separate licensing/privacy/reviewer roles.

1. For **Insider Risk Management**, review the **Risky AI usage** template,
   collection prerequisites and permitted indicators; scope a pilot and
   investigate product signals such as documented risky AI patterns [P5].
   Do not relabel the repository's keyword/volume hypotheses as IRM detections.
2. For **Communication Compliance**, use the generative-AI policy guidance
   and a restricted pilot reviewer group. Verify content exists under the
   supported collection policy and classifiers. A queued review is not an
   inline block.
3. For **eDiscovery**, an authorized case member creates a case/search over
   the applicable mailbox/AI data location and supported **Copilot activity**
   type. For collected Entra app interactions, official guidance documents
   `IPM.SkypeTeams.Message.ConnectedAIApp.Entra.<AppID>` as the ItemClass.
   Review/export through approved legal workflows, not a generic telemetry
   service principal. This repository does not automate legal content export.
4. Validate synthetic items in each selected solution separately. Disabling a
   pilot policy doesn't release legal holds or delete a review set.

## 7. Retention and deletion

1. Define separate durations for audit metadata, collected AI content,
   application traces, local spool and destination copies. Audit-retention
   policies and AI interaction retention are not the same.
2. In Data Lifecycle Management, create an approved retention policy using
   **Enterprise AI apps** for the supported custom-app collection location.
   For M365 Copilot/Studio use their documented relevant location, not this
   location by assumption.
3. Test retain/delete behavior with synthetic data. Holds and longest-retention
   conflict principles can override a shorter requested period [P5].
4. Set destination/table TTL and encrypted-spool cleanup/backup policy
   independently; Purview deletion doesn't erase exported SIEM/OTel copies.
5. Rollback changes only future policy behavior; legal/admin review is needed
   before deletion of retained content.
