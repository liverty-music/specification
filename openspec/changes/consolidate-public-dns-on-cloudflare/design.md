## Context

The liverty-music public DNS topology is currently split:

- **dev**: single Cloud DNS public zone `dev.liverty-music.app` (4 hostnames including the dev apex), with NS delegation from Cloudflare. The `web-app` service occupies the zone apex.
- **prod**: two Cloud DNS public zones (`api.liverty-music.app`, `auth.liverty-music.app`), with NS delegation from Cloudflare. The `liverty-music.app` apex stays on Cloudflare but has **no A record** — visiting `https://liverty-music.app/` resolves to Cloudflare's parking response, not to the GKE Gateway.
- **Postmark**: dev's DKIM TXT + Return-Path CNAME records are in the dev Cloud DNS zone; prod's are already directly in the Cloudflare apex zone via a separate `postmark-cloudflare-provider` block.

This asymmetry exists because the original `cloud-dns-infrastructure` design (archived 2026-05-13 `provision-prod-gcp-resources`) chose Cloud DNS for the GKE Gateway-fronted subdomains under the assumption that Google Certificate Manager's DNS authorization required Cloud DNS. The `refactor-unify-env-dispatch` (specification PR #470, cloud-provisioning PR #262) carried the asymmetry forward — its design.md Non-Goals explicitly defers the "Cloudflare apex A record" follow-up to a later change. This is that follow-up.

Two external facts make the Cloud DNS subzone pattern unjustified:

1. **Google Certificate Manager DNS authorization works with any DNS provider.** Per [Google's documentation](https://docs.cloud.google.com/certificate-manager/docs/deploy-google-managed-dns-auth): *"If you're using a third-party DNS solution to manage your DNS, refer to its documentation to add the CNAME record."* The ACME DNS-01 challenge CNAME can live in Cloudflare with no functional difference.
2. **Cloudflare Registrar requires Cloudflare nameservers at the apex.** Per [Cloudflare Registrar FAQ](https://developers.cloudflare.com/registrar/faq/): *"All domains on Cloudflare Registrar use Cloudflare nameservers."* The only escape hatch is subdomain NS delegation. Consolidating on Cloudflare eliminates the asymmetry; consolidating on Cloud DNS would require transferring the domain to a different registrar (60-day ICANN lock; loss of Cloudflare features).

Industry best practice (per investigation: Cloudflare/Cloud-DNS comparison docs, inventivehq.com DNS infra comparison) for SaaS public DNS is single-provider authoritative DNS + cloud-provider DNS for private/internal zones only. The `asia-northeast2.sql.goog` private zone (Cloud SQL PSC) stays on Cloud DNS regardless.

Stakeholders:

- **Operator** (`pannpers`): wants to ship prod by unblocking the apex serving path; tolerates dev `pulumi up` churn during the migration.
- **End users** (prod): zero today (pre-launch). After this change, end users finally reach the SPA at `https://liverty-music.app/`.
- **Future contributors**: benefit from a single Cloudflare zone as the source of truth for all public DNS — one Pulumi provider, one dashboard, no env-conditional DNS-provider routing in code.

## Goals / Non-Goals

**Goals:**

- Provision the missing prod apex A record + apex TLS certificate, unblocking `https://liverty-music.app/` serving.
- Consolidate **all** public DNS (dev + prod, all subdomains + apex, Postmark records) onto Cloudflare as the single authoritative provider.
- Eliminate the dev/prod DNS topology asymmetry: same Pulumi resource shapes, same code path, same source of truth.
- Refactor `network.ts` to remove the zone-topology indirection: delete `buildZoneTopology()`, `ZoneConfig`/`ZoneTopologyEntry` types, the per-zone provisioning loop, and the dual Cloudflare provider instances.
- Apply `protect: true` to prod-stack DNS A records and Certificate Manager resources so accidental `pulumi destroy --stack prod` cannot take production DNS down.
- Establish a manual prerequisite (Cloudflare Dashboard role lockdown) that bounds the human-error blast radius for the unified Cloudflare zone.

**Non-Goals:**

- Migrating the private Cloud SQL PSC zone (`asia-northeast2.sql.goog`). Cloud DNS private zones have no Cloudflare equivalent; this stays.
- Codifying Cloudflare member roles via `cloudflare.AccountMember` Pulumi resources. Manual runbook for now; codification is a separate change if/when the team grows.
- Enabling Cloudflare Proxy (`proxied: true` / orange-cloud) for any record. All records stay DNS-only. Future enablement (WAF, edge cache for the apex) is a separate decision.
- Splitting the Cloudflare API token per environment. Single shared admin token retained; protect:true + Dashboard role lockdown provide the operational guard.
- Touching the HTTPRoute / Gateway / Cert Manager TLS-termination layer. The Gateway already references `api-gateway-cert-map`; we add an apex CertificateMapEntry and the Gateway picks it up automatically.
- Migrating Cloud DNS for any reason other than the public zones being consolidated here. Existing `sql.goog` and `googleapis.com` private zones are untouched.
- Cross-repo follow-ups previously deferred by `refactor-unify-env-dispatch`: backend Atlas migration prod overlay, frontend `.env.prod`. Those are tracked separately.

## Decisions

### D1 — Single Cloudflare zone for all public DNS in both envs

**Decision:** Destroy all three Cloud DNS public zones (`dev.liverty-music.app`, `api.liverty-music.app`, `auth.liverty-music.app`) and the Cloudflare NS records that delegate to them. Provision every public DNS record (A records, ACME CNAMEs, Postmark DKIM/Return-Path) directly in the single Cloudflare-authoritative zone `liverty-music.app`.

**Rationale:**

- Cloudflare Registrar's apex-NS lock makes subzone delegation a permanent self-inflicted asymmetry. The only way to fully eliminate it without transferring the registrar is to embrace Cloudflare as the single public-DNS provider.
- Google Cert Manager's DNS authorization works on any DNS provider — the implicit "subzone must be Cloud DNS" assumption that justified the original split is invalid.
- Single provider = one Pulumi provider, one dashboard, one credential, one audit log to monitor. Reduces operational surface area without losing any technical capability (TLS termination remains at the GKE Gateway with Google-managed certs; Cloudflare is DNS-only).
- **Alternative considered (rejected): keep dev on Cloud DNS, migrate only prod.** Cost: dev/prod permanent asymmetry continues; the `if (environment === 'prod')` Postmark branch and the dual Cloudflare-provider pattern persist. Benefit: smaller migration blast radius. Net: rejected because the asymmetry is the root pain point; halfway fixes leave the next maintainer with the same question.
- **Alternative considered (rejected): migrate registrar away from Cloudflare and put everything on Cloud DNS.** Cost: 60-day ICANN registrar-transfer lock blocks prod launch; loss of Cloudflare features (DDoS, Pages, Workers, Email Routing) the team may want later; Cloud DNS public-zone billing (~¥30/month per zone, negligible but nonzero). Benefit: tighter GCP-native integration. Net: rejected on launch-timing alone.

### D2 — D8 naming convention from refactor-unify-env-dispatch applies to DNS resources

**Decision:** Use env-agnostic Pulumi resource names for all DNS resources. The existing convention `web-app-a-record`, `backend-server-a-record`, `zitadel-a-record`, `web-app-cert`, `web-app-dns-auth`, etc. is preserved across both stacks. Pulumi stack URN (`urn:pulumi:dev::...` vs `urn:pulumi:prod::...`) handles env disambiguation.

**Rationale:**

- Consistent with `refactor-unify-env-dispatch` decision D8 ("prod resources adopt dev's names; no per-env name suffixes"). Same code path produces same shape in every stack.
- Pulumi state is stack-scoped; identical names in different stacks do not collide. This was empirically validated by the `refactor-unify-env-dispatch` impl (PR #262) which renamed prod resources to dev's names with zero state-collision issues.
- Cloudflare DnsRecord resources benefit too: `web-app-a-record` in dev produces a record at `dev.liverty-music.app`, `web-app-a-record` in prod produces a record at `liverty-music.app` — the resource name encodes the *role*, the record content encodes the *env*.

### D3 — Phased migration: Phase A (provision new) → Phase B (cutover) → Phase C (destroy old), dev first then prod

**Decision:** Execute the migration in three logical phases per env, dev preceding prod:

- **Phase A** — provision the new Cloudflare-direct A records, ACME CNAMEs, Certs, and CertMapEntries while the Cloud DNS zones (and their Cloudflare NS delegations) remain authoritative. Verify each new Cert reaches `ACTIVE` state via Pulumi Cloud or `gcloud certificatemanager certificates describe` before continuing. Traffic is unaffected because the old A records (inside Cloud DNS, reachable via NS delegation) still serve.
- **Phase B** — destroy the Cloudflare NS-delegation records. At this moment, Cloudflare-direct A records take over authoritative answering. DNS clients see a ~30-second transition window where some resolvers may still cache old NS responses; new clients hit the new A records immediately. Pulumi destroys the old Cloud-DNS-hosted ACME CNAMEs (now unreachable) and updates `api-gateway-cert-map` to swap from the old-zone-bound cert to the new Cloudflare-zone-bound cert per hostname.
- **Phase C** — destroy the Cloud DNS public zones and the old Pulumi resources (`gcp.dns.ManagedZone`, the old `gcp.certificatemanager.Certificate` / `DnsAuthorization` resources whose CertMapEntries point at them, and the orphaned Postmark `gcp.dns.RecordSet` for dev). State is clean; the next `pulumi up` shows no diff.

**Implementation note:** Phase A and Phase B+C may be a single `pulumi up` (if dependency ordering is reliable) or split into two `pulumi up`s (safer, gives a manual checkpoint). The tasks document the split-apply path as the default; the single-apply path is available if the operator is confident.

Execute dev first → verify smoke tests → then prod.

**Rationale:**

- The new Cert resources need DNS-01 challenge resolution to issue. The Cloudflare zone is already authoritative for the apex; the NS-delegated subzones are *not* required for Cloud-DNS-hosted ACME CNAMEs to resolve, because we are creating the *new* ACME CNAMEs directly in Cloudflare during Phase A — they answer regardless of NS delegation state.
- The split-apply approach lets the operator observe Phase A's cert ACTIVE state before destroying the safety net. Single-apply works if Pulumi's dependency graph orders correctly, but the split is robust to ordering anomalies.
- Dev first is a low-stakes dress rehearsal. If Phase A or B reveals a Postmark-DKIM verification failure or a CertMap update glitch, prod is still on the old DNS and can roll back trivially.
- **Alternative considered (rejected): single-shot `pulumi up` per env with no phase split.** Cost: if anything fails mid-apply, the recovery path is to re-run `pulumi up`, but the state may be in a transient bad shape (e.g., old NS deleted but new cert not yet ACTIVE → apex briefly returns no DNS answer). Benefit: less operator coordination. Net: rejected for prod; permitted for dev where the impact is bounded.
- **Alternative considered (rejected): blue/green DNS with parallel Cert + parallel Gateway listener.** Cost: requires temporarily duplicating the GKE Gateway with a parallel static IP; much higher operational complexity. Benefit: zero-downtime cutover. Net: rejected — the ~30-second propagation window is acceptable pre-launch, and the GKE Gateway's CertMap mechanism is designed for in-place cert swaps.

### D4 — Single Cloudflare provider instance, no per-resource provider split

**Decision:** Collapse the two existing `cloudflare.Provider` instances (`postmark-cloudflare-provider` at line 161, `cloudflare-provider` at line 275 of `network.ts`) into one named `cloudflare-provider`. All Cloudflare DnsRecord resources reference this single provider via the `provider:` resource option.

**Rationale:**

- Both providers today use the same `cloudflareConfig.apiToken`. The split exists because they were introduced in different OpenSpec changes and never reconciled.
- One provider = one place to update auth, one Pulumi resource URN for the provider itself, simpler state.
- Pulumi resource name `cloudflare-provider` is the existing name and survives the consolidation without URN churn for the longer-lived instance.

### D5 — `protect: true` on prod DNS A records and all prod Certificate Manager resources; dev resources stay destroyable

**Decision:** The following prod-stack resources receive `protect: true`:

- `cloudflare.DnsRecord` for the prod apex A (`liverty-music.app`)
- `cloudflare.DnsRecord` for the prod `api` A (`api.liverty-music.app`)
- `cloudflare.DnsRecord` for the prod `auth` A (`auth.liverty-music.app`)
- All `gcp.certificatemanager.DnsAuthorization` resources in the prod stack (3 entries: web-app, backend-server, zitadel)
- All `gcp.certificatemanager.Certificate` resources in the prod stack (3 entries)
- All `gcp.certificatemanager.CertificateMapEntry` resources in the prod stack (3 entries)

Total: 12 prod resources with `protect: true`. Total prod state size in scope: ~15 resources; protect coverage = 80%. The unprotected prod resources are the ACME CNAMEs (regeneratable on re-issue) and the shared `CertificateMap` (single resource, hard to destroy accidentally because it has dependent entries).

Dev resources receive no `protect`. Dev must remain teardownable (e.g., for environment rebuild or schema-migration rollback scenarios).

**Rationale:**

- Apex A record destruction = total prod site outage. Highest blast radius, highest protect priority.
- Cert resources: destroying a Cert in active use makes the Gateway present an expired/no cert. Pulumi state recovery is non-trivial because Google-managed certs take time to re-issue.
- DnsAuthorization: tied to the Cert's ACME challenge. Destroying it forces Cert re-creation.
- CertMapEntry: detaches the Cert from the Gateway's CertMap, breaking the hostname's TLS binding.
- Per [memory `feedback_verify_review_before_merge.md`] — operational safeguards must be visible in code review, not buried in runbooks. `protect: true` is the visible signal.
- **Alternative considered (rejected): no protect, rely solely on Pulumi state isolation + manual review.** Cost: a wrong-stack `pulumi destroy` (e.g., destination flag typo on the Pulumi Cloud console) destroys prod DNS instantly. Benefit: slightly less code clutter. Net: rejected — protect:true is the cheapest possible insurance.
- **Alternative considered (rejected): also protect dev resources.** Cost: blocks legitimate `pulumi destroy --stack dev` workflows for environment rebuild. Benefit: marginal extra safety. Net: rejected — dev is intentionally destroyable.

### D6 — Cloudflare Dashboard write-permission lockdown is a manual prerequisite, not a Pulumi resource

**Decision:** Before Phase B (cutover) on prod, the operator manually changes Cloudflare Account → Members → role assignments so that all members except the break-glass operator (`pannpers`) have role "Administrator Read Only" or "DNS read only". `pannpers` retains "Super Administrator" for break-glass. This change does NOT codify Cloudflare member roles as Pulumi resources.

**Rationale:**

- The lockdown must be in effect at the moment prod traffic flips. A Pulumi-managed role would require a `pulumi up` to land before Phase B, adding another moving piece to the cutover.
- The team is currently 1 person (pannpers); the manual change is a one-time runbook step. When the team grows, codifying via `cloudflare.AccountMember` is a separate single-purpose change.
- Manual change is reversible if it locks out a needed operation; Pulumi-managed roles would require re-applying to roll back.
- **Alternative considered (rejected): codify member roles in this change.** Cost: import existing member entries into Pulumi state, manage role JSON in code, add a precondition that the change merges and applies before Phase B. Benefit: audit trail in git. Net: rejected for scope; deferred to a follow-up change.

### D7 — Single Cloudflare API token retained; no per-env split

**Decision:** Both dev and prod Pulumi stacks read the Cloudflare API token from a single ESC entry (`pulumiConfig.cloudflare.apiToken`) shared across envs. The token has `Zone:Read` + `Zone DNS:Edit` scoped to the `liverty-music.app` zone.

**Rationale:**

- With `protect: true` on prod DNS records and the dashboard lockdown in place, the Pulumi-level isolation (dev stack state cannot reference prod resources) is the primary safeguard. A second-level isolation (env-split tokens) would add token-rotation complexity without proportional benefit.
- A single rotation point reduces ops burden: rotating one ESC entry refreshes both stacks on next `pulumi up`.
- If a leak is detected, both envs are rotated simultaneously — appropriate response to a token compromise.
- **Alternative considered (rejected): per-env tokens (`pulumiConfig.cloudflare.apiToken.dev`, `.prod`).** Cost: more ESC entries to maintain; dual rotation; harder to verify "is this token still valid?". Benefit: blast radius if a dev-stack token leaks does not extend to prod. Net: rejected because the realistic leak vector (Pulumi state, CI logs) already has equivalent exposure for the GCP creds, and the token's permissions are zone-scoped read-write — already a tight blast radius.
- **Future revisit trigger:** the team grows beyond 1-2 operators OR Cloudflare introduces per-zone-section scoping (e.g., "DNS:Edit only for `*.dev.liverty-music.app`"). Document the revisit trigger in code comment near the ESC read.

### D8 — Apex serving via single-hostname certificate, mirrors the existing api/auth pattern

**Decision:** Provision the apex cert as a standalone `gcp.certificatemanager.Certificate` named `web-app-cert` (NOT `apex-cert` — D2 naming consistency with the existing dev pattern where `web-app` is the apex-occupying service in dev). Single-hostname `managed.domains: ['liverty-music.app']` (no SAN). Bind via a `web-app-cert-map-entry` to the shared `api-gateway-cert-map`. ACME DNS-01 CNAME hosted in Cloudflare at the challenge label Google assigns.

**Rationale:**

- The existing code already provisions single-hostname certs per service (see `provisionManagedHostname()` rationale in `network.ts:530-535`). Single-hostname certs avoid the "shared SAN cert replace deadlocks against in-flight CertMapEntry references" failure mode that has burned this codebase before.
- The Gateway uses `api-gateway-cert-map`; adding the apex is purely adding a new entry to that map — no Gateway-level config change.
- Reusing `web-app` as the apex service name keeps the Pulumi resource URNs aligned with dev's existing `web-app-*` URNs. Dev's `web-app` happens to also live at its zone apex (`dev.liverty-music.app` apex); the symmetry is exact.

### D9 — `SERVICES` catalog uses empty-string subdomain to denote apex, not `null` + filter

**Decision:** Replace the current `SERVICES` catalog signature:

```ts
const SERVICES: ReadonlyArray<{ name: string; subdomain: string | null }>
```

with:

```ts
const SERVICES: ReadonlyArray<{ name: string; subdomain: string }>  // '' for apex
```

The empty-string subdomain means "this service occupies the zone apex" (i.e., the hostname is the zone TLD with no prefix). The `provisionManagedHostname()` function constructs hostnames as `subdomain ? \`\${subdomain}.\${tld}\` : tld` — clean conditional, no filter.

Apex is handled in both dev and prod uniformly:

- dev: apex hostname is `dev.liverty-music.app` (the dev "apex" is itself a subdomain of the registrar TLD, but it's the apex of the dev DNS zone). After this change, the dev "apex" is just an A record at `dev` inside the Cloudflare zone.
- prod: apex hostname is `liverty-music.app`. After this change, an A record at `@` (root) inside the Cloudflare zone.

Cloudflare DnsRecord `name` field receives the full subdomain label (`dev`, `api.dev`, `auth.dev`, `@` for prod apex, `api`, `auth`).

**Rationale:**

- `null` requires a filter step (`SERVICES.filter(svc => svc.subdomain !== null)`) that prod-specifically excluded the apex. With the apex now included in prod, the filter becomes a no-op everywhere — easier to delete than to keep as a degenerate case.
- Empty string conveys "no subdomain prefix" more directly than `null`. The type narrows from `string | null` to `string` — every consumer of `subdomain` no longer needs a nullability check.
- **Alternative considered (rejected): keep `subdomain: string | null` and special-case apex inside `provisionManagedHostname()`.** Cost: keeps the nullability hazard. Benefit: marginally less code change. Net: rejected — the refactor is the right cleanup moment.

### D10 — Postmark dev migration is in-scope; DKIM TXT value must match before old record destruction

**Decision:** Remove the `if (environment === 'prod')` gate around the Postmark Cloudflare provider block (`network.ts:160-196`). Dev gains the same Postmark DKIM TXT and Return-Path CNAME records inside Cloudflare. The dev hostnames remain `{dkimSelector}._domainkey.mail.dev.liverty-music.app` and `pm-bounces.mail.dev.liverty-music.app` — only the DNS-provider authority changes.

The migration is sequenced inside the dev Phase A/B/C:

- Phase A: Create new Cloudflare-hosted Postmark records alongside the existing Cloud-DNS-hosted ones (NS delegation still authoritative for `mail.dev.liverty-music.app` via the parent `dev.liverty-music.app` zone). Postmark's domain-verification check looks up the DKIM TXT — both records exist and have identical values, so verification continues to succeed.
- Phase B: Destroy the dev Cloud DNS zone (which contains the old Postmark records). Cloudflare-hosted records become solely authoritative.
- Phase C: No additional Postmark-specific cleanup; the old records died with the parent zone.

**DKIM value mismatch is the only failure mode worth guarding.** Before Phase B, the operator runs a verification step: `dig +short TXT <selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` (Cloudflare resolver) and compares the public key to the value in `postmarkConfig.dkimPublicKey` (ESC). If they don't match, halt — Cloudflare has the wrong DKIM and Postmark email will fail verification.

**Rationale:**

- The split (dev Cloud DNS + prod Cloudflare for Postmark) is purely accidental — prod was migrated first, dev was not back-migrated. No design rationale supports keeping the split.
- Bringing dev in-scope eliminates the dual Postmark code path and the remaining env conditional.
- The DKIM TXT verification step is a 30-second `dig` check; cheap insurance against a deploy-order glitch.
- **Alternative considered (rejected): leave dev Postmark on Cloud DNS, migrate in a follow-up.** Cost: the `if (environment === 'prod')` branch persists; the dev Cloud DNS zone cannot be destroyed in Phase C (it would orphan the Postmark records). Benefit: smaller PR. Net: rejected — keeping dev Postmark on Cloud DNS forces keeping the entire dev Cloud DNS zone alive, which defeats the whole change.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| **R1: ~30s DNS propagation window at Phase B** — During the cutover, DNS resolvers with cached NS responses may briefly answer with stale records. dev users see a refresh-required gap; prod has no users today. | Time-box the Phase B operation. Operator pre-warms `1.1.1.1` and `8.8.8.8` with the new records via `dig` after Phase A. Pulumi up for Phase B runs in seconds; the propagation delay is recovery-no-action-needed. |
| **R2: Apex cert provisioning latency** (5-60 min from DnsAuthorization create to Cert ACTIVE) — Phase B is blocked until the new apex cert reaches ACTIVE state, otherwise Gateway has nothing to terminate TLS with for the apex. | Phase A explicitly waits for cert ACTIVE state via Pulumi Cloud output inspection or `gcloud certificatemanager certificates describe`. Tasks include this checkpoint. Pulumi Cloud's manual-trigger model for prod naturally enforces the wait. |
| **R3: Postmark DKIM verification gap** — If the new Cloudflare DKIM TXT contains a different public key value than what's stored in `postmarkConfig.dkimPublicKey`, Postmark's domain check fails after Phase B and emails fail to send. | DKIM value-verification dig step in tasks before Phase B. The same `postmarkConfig.dkimPublicKey` ESC value seeds both records — values should be byte-equivalent. The mismatch only occurs if ESC has been re-rotated since the Cloud DNS record was created and the Cloud DNS record was never updated. |
| **R4: Cloud DNS state cleanup must complete before next `pulumi up`** — If Phase C's Pulumi destroy is interrupted (e.g., transient API error mid-destroy), stale `gcp.dns.ManagedZone` references in state trigger drift errors on subsequent `pulumi up`. | Phase C re-run is idempotent. Operator re-runs `pulumi up` until clean. If a zone destroy is permanently stuck (e.g., zone has non-Pulumi-managed records that block deletion), operator manually clears non-managed records via `gcloud dns record-sets delete`, then re-runs Pulumi. |
| **R5: Cloudflare API rate limits** — Free-tier limit is 1200 API calls per 5 minutes per account. Phase A creates ~15-20 resources in a single `pulumi up`. Well within limits, but documented for safety. | Phase A creates batched in single Pulumi up; Pulumi internally rate-limits resource API calls. If hit, Pulumi retries with exponential backoff. No special handling needed. |
| **R6: Cloudflare-only public DNS = no DNS-level redundancy** — If Cloudflare DNS is fully unavailable, all public resolution fails. Cloud DNS subzones today would not survive Cloudflare's apex outage either (NS chain breaks at the apex), so this is a no-change to the SPOF reality. | Accepted. Cloudflare DNS SLA is 100% with credit. Adding a secondary DNS provider (e.g., Route53 as backup NS) is a separate hardening change post-launch, gated on observed need. |
| **R7: Gateway listener temporarily presents wrong cert during the CertMapEntry swap** — When Pulumi updates `api-gateway-cert-map` in Phase B to swap from old-zone-bound Cert to new-zone-bound Cert per hostname, there is a sub-second window where the Gateway may serve a 502 or stale cert. | The Google Gateway controller applies CertMap updates atomically per hostname; the swap is closer to "two certs valid simultaneously briefly, then old detached" than to "old gone, new not yet attached". Window is sub-second per hostname and not user-visible at pre-launch traffic levels. |
| **R8: Operator forgets manual Cloudflare Dashboard role lockdown** — D6 is a manual step; if skipped, the unified Cloudflare zone is editable by all team members (currently 1, but adds risk as team grows). | Tasks include the lockdown as an explicit checklist item with operator-attended status. The operator confirms completion before Phase B prod cutover. |

## Migration Plan

**Phase 0 — Pre-flight (out-of-band)**

1. Confirm `pulumi up --stack prod` for `refactor-unify-env-dispatch` (cloud-provisioning PR #262) has been applied — verify via Pulumi Cloud console that prod state contains unified `Zitadel$...` URNs (not `BackendMachineKey$...` URNs). If not, **halt** — apply that first; this change depends on the unified state.
2. Confirm the prod backend Pod is healthy post-refactor-deploy (`kubectl -n backend get pods --context prod` shows `Running` 1/1).
3. Cloudflare Dashboard → Manage Account → Members: change all non-pannpers members to "Administrator Read Only" or remove. Confirm pannpers retains Super Administrator. Document the state change in the PR description.

**Phase A — Provision new (per env, dev first then prod)**

4. Open the cloud-provisioning impl PR. Pulumi preview shows for dev: ~10 creates (3 service A records + 3 ACME CNAMEs + 1 apex cert + 1 apex DnsAuth + 1 apex CertMapEntry + Postmark records); no destroys yet (Phase A leaves old state intact).
5. For prod: ~7-8 creates (apex Cert + DnsAuth + A + CertMapEntry; 2 new ACME CNAMEs for api/auth in Cloudflare; the api/auth A records already exist in Cloud DNS but new direct ones get added in Cloudflare).
6. Merge PR. Dev `pulumi up` auto-runs via Pulumi Cloud Deployments.
7. Verify dev Phase A: `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-dev` → state `ACTIVE`.
8. Operator triggers `pulumi up --stack prod` via Pulumi Cloud console (manual per `deployment-infrastructure` requirement).
9. Verify prod Phase A: apex cert ACTIVE; api/auth new direct Cloudflare A records exist; old Cloud-DNS A records still present (both serving — NS-delegated chain still resolves).

**Phase B + C — Cutover and cleanup (per env, dev first)**

10. Open a follow-up impl PR (or the same PR with phase-B/C tasks gated behind an ESC flag — tasks document the recommended split). The follow-up Pulumi preview shows for dev: 1 destroy on the Cloud DNS zone + 4 destroys on NS-delegation records + 2 destroys on old Postmark records + 1 update on the dev CertMap (swap to new CertMapEntries).
11. Pre-cutover verification (dev): `dig +short TXT <selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` returns the new key matching ESC. If mismatch, **halt**.
12. Merge follow-up PR. Dev `pulumi up` runs cutover.
13. Verify dev: `dig liverty-music.app @1.1.1.1` returns the GKE static IP. `curl -I https://dev.liverty-music.app/` returns 200. `curl -I https://api.dev.liverty-music.app/grpc.health.v1.Health/Check` returns 200. Postmark sends a test email from dev backend; arrives within 60s.
14. Operator triggers `pulumi up --stack prod` for cutover.
15. Verify prod: `curl -I https://liverty-music.app/` returns 200 (SPA serves). `curl -I https://api.liverty-music.app/` returns 200. `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` returns 200 (Zitadel). Apex cert presented matches `liverty-music.app`.

**Rollback Strategy**

- **If Phase A fails to ACTIVE within 60 min**: Cert provisioning is gated on Cloudflare-published ACME CNAME being reachable. Diagnose by `dig` against the challenge label Google logged. If Cloudflare record exists but Google can't see it, contact GCP support — the ACME challenge resolver should work. Worst case: destroy and re-create the DnsAuthorization (forces a fresh challenge label).
- **If Phase B reveals a user-visible outage on dev**: revert the Phase B/C PR. Dev's Cloud DNS zone still exists (Phase C didn't run), so re-creating the NS delegation in Cloudflare brings dev DNS back. Postmark DKIM stays on the new Cloudflare value, which is correct.
- **If Phase B+C succeeds on dev but Phase B fails on prod**: prod is mid-cutover. Cloudflare apex A is up; Cloud DNS subzones are gone. If the apex A is wrong (typo in static IP), operator manually edits the A record value via Pulumi (the resource is `protect: true` but mutation is allowed) and re-runs `pulumi up`. If the cert is wrong, operator destroys the CertMapEntry and re-creates pointing to a valid cert.

## Open Questions

- **OQ1: Should the apex cert provisioning use the same `gcp.certificatemanager.Certificate` Google-managed flow, or use a Cloudflare Origin Certificate (15-year self-signed by Cloudflare, presented to clients via Cloudflare proxy)?** Recommendation: stick with Google-managed (no proxy in scope per Non-Goals; Cloudflare Origin Cert requires `proxied: true`). Revisit when Cloudflare Proxy is introduced.
- **OQ2: Should the `protect: true` annotations be applied only via `pulumi.CustomResourceOptions { protect: true }` per-resource, or by extracting a `protectInProd()` helper?** Recommendation: per-resource for explicitness — 12 occurrences is below the threshold where a helper improves readability. Reconsider if the protected-resource count grows beyond 20.
- **OQ3: Should Postmark Return-Path records be at `pm-bounces.mail` (dev) or moved to apex `pm-bounces`?** Today dev uses `pm-bounces.mail.dev.liverty-music.app`; prod uses `pm-bounces.mail.liverty-music.app`. Recommendation: keep the existing hostnames unchanged in this change; consolidating to apex is a separate Postmark-domain-config change that requires re-verifying the sender domain on Postmark side.
- **OQ4: When should Cloudflare Proxy (`proxied: true` / orange-cloud) be enabled?** Out of scope for this change. Decision point: when WAF / edge-cache value exceeds the gRPC-incompatibility cost (Connect-RPC streaming over CF Free/Pro = broken; needs Business+ plan). Document the trigger in a follow-up `enable-cloudflare-proxy` proposal.
