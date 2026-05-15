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
- Modifying HTTPRoute YAML in k8s overlays. The prod apex hostname binding (`hostnames: ['liverty-music.app']` on the prod frontend HTTPRoute) was already configured by the prior `prod-k8s-manifests` change (archived 2026-05-14) — this change does **not** author or edit any HTTPRoute resource, only consumes the existing binding. A pre-flight verification task confirms the binding is in place before cutover. The Gateway already references `api-gateway-cert-map`; we add an apex `CertificateMapEntry` (Cert Manager GCP resource, not HTTPRoute YAML) and the Gateway picks it up automatically.
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

### D3 — Single-apply migration per env, dev first then prod

**Decision:** Execute the migration as **a single `pulumi up` per env** (single-apply), dev preceding prod. Each per-env `pulumi up` creates the new Cloudflare-direct A records / ACME CNAMEs / apex Cert chain AND destroys the old Cloud DNS public zones, NS-delegation records, and the now-orphaned `gcp.dns.RecordSet` resources inside those zones in one transaction. Pulumi's dependency graph orders the creates ahead of the destroys; the new Cert reaches `ACTIVE` (DNS-01 challenge resolved via the new Cloudflare CNAME) before the old A record is destroyed.

**Cutover window per env**: ~30 seconds of DNS propagation while clients with cached NS responses transition from the old Cloud-DNS-chained answer to the new Cloudflare-direct answer. Pulumi up itself completes in seconds for the DNS resource swap; the propagation tail is recovery-no-action-needed.

Execute dev first → verify smoke tests → then operator manually triggers prod via Pulumi Cloud console (per `deployment-infrastructure` capability requirement).

**Rationale:**

- The new Cert resources need DNS-01 challenge resolution to issue. The Cloudflare zone is already authoritative for the apex; the new ACME CNAMEs are created directly in Cloudflare during the same apply that creates the new Cert/DnsAuthorization, so they resolve regardless of the old NS-delegation state. Pulumi correctly orders `cloudflare.DnsRecord(ACME CNAME)` → `gcp.certificatemanager.Certificate` so that cert ACTIVE state is achievable before the old infrastructure is torn down.
- **Pre-launch traffic shape**: prod has zero real users today. A ~30s DNS propagation window during single-apply is operationally invisible. Post-launch, this would not be acceptable and a split-apply approach would be reconsidered — but the pre-launch destructive window is the right moment for the simpler path.
- Dev first is a low-stakes dress rehearsal. If the dev apply reveals a Postmark-DKIM verification failure or a CertMap update glitch, prod is still on the old DNS and recovery is reverting the dev apply via re-run (see Rollback Strategy).
- **Alternative considered (rejected): split-apply via Phase A (provision new in parallel) → Phase B (destroy NS delegation) → Phase C (cleanup) across two PRs.** Cost: doubles the operator coordination (two PR cycles, two `pulumi up`s per env, four total prod apply windows); requires `network.ts` to temporarily host both Cloud DNS and Cloudflare-direct provisioning paths in parallel during Phase A, increasing code complexity. Benefit: lets the operator observe Phase A cert ACTIVE state before destroying the safety net. Net: rejected — pre-launch zero-user traffic shape eliminates the value of the safety net, and Pulumi's dependency graph already enforces create-before-destroy ordering for the Cert ACTIVE invariant.
- **Alternative considered (rejected): blue/green DNS with parallel Cert + parallel Gateway listener.** Cost: requires temporarily duplicating the GKE Gateway with a parallel static IP; much higher operational complexity. Benefit: zero-downtime cutover. Net: rejected — the ~30s window is acceptable pre-launch, and the GKE Gateway's CertMap mechanism is designed for in-place cert swaps.

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

**Decision:** Before the prod `pulumi up`, the operator manually changes Cloudflare Account → Members → role assignments so that all members except the break-glass operator (`pannpers`) have role "Administrator Read Only" or "DNS read only". `pannpers` retains "Super Administrator" for break-glass. This change does NOT codify Cloudflare member roles as Pulumi resources.

**Rationale:**

- The lockdown must be in effect at the moment prod traffic flips. A Pulumi-managed role would require a `pulumi up` to land before the prod DNS apply, adding another moving piece to the cutover.
- The team is currently 1 person (pannpers); the manual change is a one-time runbook step. When the team grows, codifying via `cloudflare.AccountMember` is a separate single-purpose change.
- Manual change is reversible if it locks out a needed operation; Pulumi-managed roles would require re-applying to roll back.
- **Alternative considered (rejected): codify member roles in this change.** Cost: import existing member entries into Pulumi state, manage role JSON in code, add a precondition that the change merges and applies before the prod DNS apply. Benefit: audit trail in git. Net: rejected for scope; deferred to a follow-up change.

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

The migration runs inside the dev single-apply (per D3): the Pulumi up that destroys the dev Cloud DNS zone (which contains the old Postmark records) also creates the new Cloudflare-hosted Postmark records in the same transaction. Because the new records carry the same DKIM public key value (sourced from the same `postmarkConfig.dkimPublicKey` ESC entry), Postmark's domain-verification check continues to succeed across the cutover — the only constraint is that the DKIM TXT value in Cloudflare matches what Postmark recorded at sender-domain enrollment.

**DKIM value mismatch is the only failure mode worth guarding.** Before merging the PR that triggers the dev `pulumi up`, the operator runs a verification step: `dig +short TXT <selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` (Cloudflare resolver) and compares the public key to the value in `postmarkConfig.dkimPublicKey` (ESC). If they don't match, halt — Cloudflare has the wrong DKIM and Postmark email will fail verification post-apply.

**Rationale:**

- The split (dev Cloud DNS + prod Cloudflare for Postmark) is purely accidental — prod was migrated first, dev was not back-migrated. No design rationale supports keeping the split.
- Bringing dev in-scope eliminates the dual Postmark code path and the remaining env conditional.
- The DKIM TXT verification step is a 30-second `dig` check; cheap insurance against a deploy-order glitch.
- **Alternative considered (rejected): leave dev Postmark on Cloud DNS, migrate in a follow-up.** Cost: the `if (environment === 'prod')` branch persists; the dev Cloud DNS zone cannot be destroyed in the single-apply (it would orphan the Postmark records). Benefit: smaller PR. Net: rejected — keeping dev Postmark on Cloud DNS forces keeping the entire dev Cloud DNS zone alive, which defeats the whole change.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| **R1: ~30s DNS propagation window at cutover** — During the per-env `pulumi up`, DNS resolvers with cached NS responses may briefly answer with stale records. dev users see a refresh-required gap; prod has no users today. | Pulumi up itself completes in seconds for the DNS resource swap. Operator can pre-warm `1.1.1.1` and `8.8.8.8` with `dig` immediately after apply to confirm propagation. The tail is recovery-no-action-needed. |
| **R2: Apex cert provisioning latency** (5-60 min from DnsAuthorization create to Cert ACTIVE) — The new apex Cert depends on the new Cloudflare-hosted ACME CNAME being resolvable. Pulumi's dependency graph orders `cloudflare.DnsRecord(CNAME)` → `gcp.certificatemanager.Certificate`, but Google's ACME validator may take up to 60 min to observe the CNAME and mark the cert ACTIVE. During this window, the Gateway has no apex cert to terminate TLS with. | Post-apply verification (tasks §11.2) waits for `gcloud certificatemanager certificates describe web-app-cert --format='value(managed.state)' = ACTIVE` before declaring cutover complete. The new apex A record + DnsAuthorization are provisioned in the same apply that creates the cert, so the validator has everything it needs from the moment Pulumi up completes. |
| **R3: Postmark DKIM verification gap** — If the new Cloudflare DKIM TXT contains a different public key value than what's stored in `postmarkConfig.dkimPublicKey`, Postmark's domain check fails after the dev apply and emails fail to send. | DKIM value-verification `dig` step gates the merge (tasks §10.1). The same `postmarkConfig.dkimPublicKey` ESC value seeds both records — values should be byte-equivalent. The mismatch only occurs if ESC has been re-rotated since the Cloud DNS record was created and the Cloud DNS record was never updated. |
| **R4: Cloud DNS state cleanup must complete in single-apply** — If the destroy half of the single-apply is interrupted (e.g., transient API error mid-destroy), stale `gcp.dns.ManagedZone` references in state trigger drift errors on subsequent `pulumi up`. | `pulumi up` re-run is idempotent — destroyed resources stay destroyed, missing creates are added, partial deletes complete. Operator re-runs `pulumi up` until clean. If a zone destroy is permanently stuck (e.g., zone has non-Pulumi-managed records that block deletion), operator manually clears non-managed records via `gcloud dns record-sets delete`, then re-runs Pulumi. |
| **R5: Cloudflare API rate limits** — Free-tier limit is 1200 API calls per 5 minutes per account. Single-apply creates ~15-20 resources per env. Well within limits, but documented for safety. | Single-apply uses one Pulumi up that batches resource creates; Pulumi internally rate-limits API calls. If hit, Pulumi retries with exponential backoff. No special handling needed. |
| **R6: Cloudflare-only public DNS = no DNS-level redundancy** — If Cloudflare DNS is fully unavailable, all public resolution fails. Cloud DNS subzones today would not survive Cloudflare's apex outage either (NS chain breaks at the apex), so this is a no-change to the SPOF reality. | Accepted. Cloudflare DNS SLA is 100% with credit. Adding a secondary DNS provider (e.g., Route53 as backup NS) is a separate hardening change post-launch, gated on observed need. |
| **R7: Gateway listener temporarily presents wrong cert during the CertMapEntry swap** — When Pulumi updates `api-gateway-cert-map` to swap from old-zone-bound Cert to new-zone-bound Cert per hostname during the apply, there is a sub-second window where the Gateway may serve a 502 or stale cert. | The Google Gateway controller applies CertMap updates atomically per hostname; the swap is closer to "two certs valid simultaneously briefly, then old detached" than to "old gone, new not yet attached". Window is sub-second per hostname and not user-visible at pre-launch traffic levels. |
| **R8: Operator forgets manual Cloudflare Dashboard role lockdown** — D6 is a manual step; if skipped, the unified Cloudflare zone is editable by all team members (currently 1, but adds risk as team grows). | Tasks include the lockdown as an explicit checklist item with operator-attended status. The operator confirms completion before the prod apply trigger. |

## Migration Plan

**Phase 0 — Pre-flight (out-of-band)**

1. Confirm `pulumi up --stack prod` for `refactor-unify-env-dispatch` (cloud-provisioning PR #262) has been applied — verify via Pulumi Cloud console that prod state contains unified `Zitadel$...` URNs (not `BackendMachineKey$...` URNs). If not, **halt** — apply that first; this change depends on the unified state.
2. Confirm the prod backend Pod is healthy post-refactor-deploy (`kubectl -n backend get pods --context prod` shows `Running` 1/1).
3. Cloudflare Dashboard → Manage Account → Members: change all non-pannpers members to "Administrator Read Only" or remove. Confirm pannpers retains Super Administrator. Document the state change in the PR description.

**Phase 1 — Dev single-apply (automatic on PR merge)**

4. Open the cloud-provisioning impl PR. Pulumi preview shows for dev: ~14 creates (3 service A records + 3 ACME CNAMEs + 3 apex Cert chain resources [cert + dns-auth + cert-map-entry] + 2 Cloudflare Postmark records + reused dnsAuthorization/cert references for the existing api/auth services that get rebound to the new Cloudflare ACME CNAMEs) + ~7 destroys (1 ManagedZone + 4 NS-delegation Cloudflare records + 2 dev Postmark `gcp.dns.RecordSet`; the 6 internal `gcp.dns.RecordSet` resources die together with the zone) + ~1 update on `api-gateway-cert-map`.
5. For prod: ~9 creates (3 Cloudflare A records for apex/api/auth + 3 ACME CNAMEs + 3 new apex Cert chain resources) + ~11 destroys (2 ManagedZones + 6 NS-delegation Cloudflare records + 3 old api/auth `gcp.dns.RecordSet`) + ~1 update on `api-gateway-cert-map` (gains apex entry).
6. Pre-merge DKIM verification (dev): `dig +short TXT <selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` returns the current public key matching `pulumiConfig.postmark.dkimPublicKey` in ESC. If mismatch, **halt** — investigate before merging.
7. Merge PR. Dev `pulumi up` auto-runs via Pulumi Cloud Deployments. The apply creates the new Cloudflare resources and destroys the Cloud DNS public zone in one transaction. Pulumi's dependency graph ensures new ACME CNAMEs exist before the old ones are torn down.
8. Verify dev: `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-dev --format='value(managed.state)'` returns `ACTIVE` (wait up to 60 min). `dig liverty-music.app @1.1.1.1` returns the dev `api-gateway-static-ip` served by Cloudflare authoritative. `curl -I https://dev.liverty-music.app/` returns 200. `curl -I https://api.dev.liverty-music.app/grpc.health.v1.Health/Check` returns 200 or auth-required (not a TLS error). Postmark dashboard shows `mail.dev.liverty-music.app` sender domain verified.

**Phase 2 — Prod single-apply (manual trigger)**

9. Operator triggers `pulumi up --stack prod` via Pulumi Cloud console (manual per `deployment-infrastructure` requirement). Operator reviews the preview's destroy list — especially confirming no `+- replace` on api/auth Cert resources (would indicate a `managed.domains` change that would deadlock against the existing CertMapEntry).
10. Verify prod: `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-prod --format='value(managed.state)'` returns `ACTIVE`. `curl -I https://liverty-music.app/` returns 200 (apex SPA loads). `dig +short A liverty-music.app @1.1.1.1` returns the prod `api-gateway-static-ip`. `openssl s_client -connect liverty-music.app:443 -servername liverty-music.app` shows cert issuer Google Trust Services (not Cloudflare Universal SSL). `curl -I https://api.liverty-music.app/` and `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` both return 200.

**Rollback Strategy**

The single-apply path destroys old infrastructure in the same transaction as creating new infrastructure. Rollback options after the apply has run are limited — there is no "old state preserved as safety net" by design. Per R1/R2, failure modes during the apply are recoverable by re-running `pulumi up`; failure modes detected after the apply require active recovery, not revert.

- **If the apply itself fails mid-transaction** (transient API error, runner kill, etc.): re-run `pulumi up` for the same env. Pulumi's destroy + create is idempotent — destroyed resources stay destroyed, missing creates are added, the apply resumes from the failed step. This is the primary recovery path.
- **If the new apex Cert fails to reach ACTIVE within 60 min**: diagnose by `dig` against the Google-emitted ACME challenge label (`gcloud certificatemanager dns-authorizations describe web-app-dns-auth`). If the Cloudflare CNAME exists but Google's validator cannot resolve it, contact GCP support. Worst-case recovery: destroy and re-create the DnsAuthorization via Pulumi (`pulumi destroy --target ...DnsAuthorization::web-app-dns-auth && pulumi up`) — forces a fresh challenge label.
- **If a post-apply user-visible outage is detected on dev** (e.g., apex returns NXDOMAIN after Pulumi success): the dev Cloud DNS zone is already gone — `pulumi destroy` against the new Cloudflare records would leave the env entirely without DNS. Recovery: identify the misconfigured Pulumi resource, fix the source code, push a hotfix PR. Dev's pre-launch traffic shape makes "dev down for a few hours" tolerable.
- **If a post-apply outage is detected on prod**: same recovery path as dev — fix source, push hotfix. The `protect: true` flags on prod DNS/cert resources prevent accidental destroy; the operator can still mutate values via `pulumi up` (protect only blocks destroy, not update). For an apex A record value typo, the fix lands via a one-line source change + re-apply. For a wrong cert, destroy the CertMapEntry (not protect-blocked since the swap is an update) and re-create pointing to a corrected cert.
- **If both dev and prod fail in the same way**: revert the PR. The hotfix PR re-applies the change minus the bug. Note that *reverting the merge alone does not restore old Cloud DNS state* — that infrastructure is gone. The revert simply prevents further damage; positive recovery still requires running `pulumi up` against the corrected source.

## Open Questions

- **OQ1: Should the apex cert provisioning use the same `gcp.certificatemanager.Certificate` Google-managed flow, or use a Cloudflare Origin Certificate (15-year self-signed by Cloudflare, presented to clients via Cloudflare proxy)?** Recommendation: stick with Google-managed (no proxy in scope per Non-Goals; Cloudflare Origin Cert requires `proxied: true`). Revisit when Cloudflare Proxy is introduced.
- **OQ2: Should the `protect: true` annotations be applied only via `pulumi.CustomResourceOptions { protect: true }` per-resource, or by extracting a `protectInProd()` helper?** Recommendation: per-resource for explicitness — 12 occurrences is below the threshold where a helper improves readability. Reconsider if the protected-resource count grows beyond 20.
- **OQ3: Should Postmark Return-Path records be at `pm-bounces.mail` (dev) or moved to apex `pm-bounces`?** Today dev uses `pm-bounces.mail.dev.liverty-music.app`; prod uses `pm-bounces.mail.liverty-music.app`. Recommendation: keep the existing hostnames unchanged in this change; consolidating to apex is a separate Postmark-domain-config change that requires re-verifying the sender domain on Postmark side.
- **OQ4: When should Cloudflare Proxy (`proxied: true` / orange-cloud) be enabled?** Out of scope for this change. Decision point: when WAF / edge-cache value exceeds the gRPC-incompatibility cost (Connect-RPC streaming over CF Free/Pro = broken; needs Business+ plan). Document the trigger in a follow-up `enable-cloudflare-proxy` proposal.
