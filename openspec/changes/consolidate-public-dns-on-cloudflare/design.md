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

**Decision:** Execute the migration as **a single `pulumi up` per env** (single-apply), dev preceding prod. Each per-env `pulumi up` creates the new Cloudflare-direct A records / ACME CNAMEs / apex Cert chain AND destroys the old Cloud DNS public zones, NS-delegation records, and the now-orphaned `gcp.dns.RecordSet` resources inside those zones in one transaction.

**Pulumi ordering caveat**: dependency-graph ordering is enforced *only* where Pulumi sees an input reference between two resources. The migration has two distinct ordering cases:

- **Apex `web-app-*` Cert chain (prod only)**: genuinely new resources chained via input references (`gcp.certificatemanager.DnsAuthorization.dnsResourceRecords` → `cloudflare.DnsRecord(ACME CNAME)`; `DnsAuthorization` → `gcp.certificatemanager.Certificate.managed.dnsAuthorizations`). Pulumi enforces create-before-validate ordering; the new Cert reaches `ACTIVE` only after the new CNAME is reachable. Safe.
- **api/auth ACME CNAME flip (both envs) + web-app/backend-server/zitadel ACME CNAME flip (dev)**: the new `cloudflare.DnsRecord/${name}-dns-auth-cname` and the old `gcp.dns.RecordSet/${name}-dns-auth-cname` share a Pulumi resource *name* but differ in resource *type*; Pulumi has no input-reference edge between them, so destroy(old) and create(new) may execute in parallel. A brief window where neither ACME CNAME exists is possible. This race is documented in R7 with its practical mitigation (ACME re-validation interval is ~24h vs Pulumi apply window of seconds; operator post-apply `dig` confirms reachability).

**Cutover window per env**: Pulumi up itself completes in seconds for the DNS resource swap, but the **propagation tail is bounded by the existing Cloudflare NS-record TTL** delegating the affected subzone to Cloud DNS. Current NS TTL is **3600 seconds (1 hour)** per `network.ts`'s NS-delegation block. Resolvers that have already cached those NS RRsets continue querying the Cloud DNS nameservers until cache expiry; once Pulumi destroys the Cloud DNS `ManagedZone` in the same apply, those cached resolvers receive `SERVFAIL`/`REFUSED` for the remainder of their cached NS TTL. To minimize this tail, an optional pre-cutover task (tasks.md §1.8) lowers the NS TTL to 60 s and waits one full TTL period before the destructive apply runs. Skipping the pre-cutover task is acceptable for the current pre-launch environment (zero real prod users; dev developers tolerate a refresh-required gap).

**NS-vs-A coexistence at the same Cloudflare name**: For `api.liverty-music.app`, `auth.liverty-music.app`, and `dev.liverty-music.app`, the apply simultaneously destroys the existing Cloudflare NS-delegation records AND creates new Cloudflare A records at the same names. Per DNS RFC, NS and A records cannot coexist at the same non-apex name. Cloudflare's API enforces this — a `create A at name with existing NS` call returns an error. Pulumi has no input-reference edge between the new A record and the old NS records (different types, no shared output), so it may attempt create-before-destroy and hit the API error. Practical outcome: the first `pulumi up` may fail partway with a Cloudflare API error; re-running `pulumi up` after the NS destroys complete succeeds. Operator should be prepared for a possible second apply.

Execute dev first → verify smoke tests → then operator manually triggers prod via Pulumi Cloud console (per `deployment-infrastructure` capability requirement).

**Rationale:**

- The new Cert resources need DNS-01 challenge resolution to issue. The Cloudflare zone is already authoritative for the apex; the new ACME CNAMEs are created directly in Cloudflare during the same apply that creates the new Cert/DnsAuthorization, so they resolve regardless of the old NS-delegation state. For the apex chain (genuinely new resources), Pulumi orders `gcp.certificatemanager.DnsAuthorization` → `cloudflare.DnsRecord(ACME CNAME)` → `gcp.certificatemanager.Certificate` via input references, so cert ACTIVE state is achievable as soon as Google's validator observes the new CNAME. For the api/auth case (existing chain whose ACME CNAME backing resource flips type), see the Pulumi ordering caveat above and R7 — the race is real but the practical collision probability is small.
- **Pre-launch traffic shape**: prod has zero real users today. A ~30s DNS propagation window during single-apply is operationally invisible. Post-launch, this would not be acceptable and a split-apply approach would be reconsidered — but the pre-launch destructive window is the right moment for the simpler path.
- Dev first is a low-stakes dress rehearsal. If the dev apply reveals a Postmark-DKIM verification failure or a CertMap update glitch, prod is still on the old DNS and recovery is reverting the dev apply via re-run (see Rollback Strategy).
- **Alternative considered (rejected): split-apply via Phase A (provision new in parallel) → Phase B (destroy NS delegation) → Phase C (cleanup) across two PRs.** Cost: doubles the operator coordination (two PR cycles, two `pulumi up`s per env, four total prod apply windows); requires `network.ts` to temporarily host both Cloud DNS and Cloudflare-direct provisioning paths in parallel during Phase A, increasing code complexity. Benefit: lets the operator observe Phase A cert ACTIVE state before destroying the safety net, AND eliminates the api/auth ACME CNAME flip race documented in R7 (because new and old records coexist during Phase A so no gap window exists). Net: rejected — pre-launch zero-user traffic shape eliminates the value of the safety net, and the R7 race window is bounded to seconds against a ~24h ACME re-validation interval, making collision unlikely in practice.
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

Total: 12 prod resources with `protect: true`. Total prod state size in scope: ~16 resources; protect coverage = 75%. The unprotected prod resources are the 3 ACME CNAMEs (regeneratable on re-issue) and the shared `CertificateMap` (single resource, hard to destroy accidentally because it has dependent entries).

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
| **R1: DNS propagation window bounded by NS-record TTL at cutover** — During the per-env `pulumi up`, DNS resolvers with cached NS responses continue querying the soon-to-be-destroyed Cloud DNS nameservers until cache expiry. The current NS-delegation record TTL is **3600 seconds (1 hour)** (set in `network.ts` via `ttl: 3600` on the NS Cloudflare DnsRecord). Once Pulumi destroys the Cloud DNS `ManagedZone` in the same apply, cached resolvers receive `SERVFAIL`/`REFUSED` for up to 1 hour. dev users see a refresh-required gap; prod has no real users today (pre-launch). | **Optional pre-cutover task** (tasks.md §1.8): lower the NS-delegation TTL to 60 s and wait one full TTL period (1 hour) before merging the impl PR — this caps the propagation tail at ~60 s. **Skipping** the pre-cutover task is acceptable for the current pre-launch state and is the default for this change. Operator post-apply: `dig +short A api.liverty-music.app @1.1.1.1 @8.8.8.8` to confirm new Cloudflare-direct answer is reachable. The propagation tail is recovery-no-action-needed; cached clients refresh on their own schedule. |
| **R1b: NS-vs-A Cloudflare API conflict at the same name** — For `api.liverty-music.app`, `auth.liverty-music.app`, and `dev.liverty-music.app`, the apply simultaneously destroys the existing Cloudflare NS-delegation records and creates new Cloudflare A records at the same names. Per DNS RFC, NS and A cannot coexist at the same non-apex name; Cloudflare's API enforces this and returns an error on `create A` while NS still exists. Pulumi has no input-reference edge between the new A record and the old NS records (different types, no shared output), so it may attempt create-before-destroy and the create call fails. | First `pulumi up` may fail partway with `Cloudflare API error: A record at <name> conflicts with existing NS records`. Re-running `pulumi up` after the NS destroys complete succeeds — Pulumi's plan is idempotent. Operator should be prepared for one re-run. If the failure repeats after multiple re-applies, manually delete the NS records via `cloudflare api dns_records ...` (or the dashboard) and re-run Pulumi. |
| **R2: Apex cert provisioning latency** (5-60 min from DnsAuthorization create to Cert ACTIVE) — The new apex Cert depends on the new Cloudflare-hosted ACME CNAME being resolvable. Pulumi's dependency graph orders `cloudflare.DnsRecord(CNAME)` → `gcp.certificatemanager.Certificate`, but Google's ACME validator may take up to 60 min to observe the CNAME and mark the cert ACTIVE. During this window, the Gateway has no apex cert to terminate TLS with, and `https://liverty-music.app/` returns a TLS error to any client. | Default mitigation: post-apply verification (tasks §11.2) waits for `gcloud certificatemanager certificates describe web-app-cert --format='value(managed.state)' = ACTIVE` before declaring cutover complete. The new apex A record + DnsAuthorization are provisioned in the same apply that creates the cert, so the validator has everything it needs from the moment Pulumi up completes. **Optional fast-path for zero-TLS-error-window**: pre-issue the apex Cert in a preparatory PR before the main cutover PR — provision `web-app-dns-auth` + the apex Cloudflare ACME CNAME + `web-app-cert` + `web-app-cert-map-entry` first, wait for `state: ACTIVE`, then merge the main PR that adds the apex A record + destroys Cloud DNS. By the time the A record resolves to the prod Gateway, the apex Cert is already ACTIVE. The current change does **not** use this fast-path — accepted up-to-60-min window is operationally invisible at pre-launch (zero apex users). Pre-issue is the recommended path for any post-launch redo of this cutover. |
| **R3: Postmark DKIM verification gap (dev)** — If the new Cloudflare DKIM TXT contains a different public key value than what's stored in `postmarkConfig.dkimPublicKey`, Postmark's domain check fails after the dev apply and emails fail to send. | DKIM value-verification `dig` step gates the merge (tasks §10.1). The same `postmarkConfig.dkimPublicKey` ESC value seeds both records — values should be byte-equivalent. The mismatch only occurs if ESC has been re-rotated since the Cloud DNS record was created and the Cloud DNS record was never updated. |
| **R3b: Prod Postmark force-replace race (D4 provider consolidation)** — Per D4 / §5.1, the prod `postmark-cloudflare-provider` is deleted and the 2 prod Postmark `cloudflare.DnsRecord` resources (DKIM TXT + Return-Path CNAME) are re-parented to the consolidated `cloudflare-provider`. Pulumi treats a `provider:` URN change as a replace operation (destroy + create); there is no input-reference edge between the old and new records, so the same parallel-execution race documented in R7 (ACME CNAME flip) applies here. A brief window where the prod DKIM TXT or Return-Path CNAME is missing could cause transactional email DKIM verification failures while clients query during the window. | Postmark uses periodic re-verification of sender domains (not per-message; the verified status persists once established), so the practical collision probability is low. Operator post-apply verification (added to tasks §11.2): `dig +short TXT <selector>._domainkey.mail.liverty-music.app @1.1.1.1` returns the expected DKIM public key value, and `dig +short CNAME pm-bounces.mail.liverty-music.app @1.1.1.1` returns `pm.mtasv.net`. Post-apply smoke (added to tasks §12.3): trigger a prod-backend test email and confirm delivery via Postmark dashboard. If Postmark dashboard shows the sender domain in `Pending verification` or `Verification failed` state post-apply, run `Verify DKIM` action in the Postmark dashboard to force re-check. The fix is operator-attended and recoverable without code change. |
| **R4: Cloud DNS state cleanup must complete in single-apply** — If the destroy half of the single-apply is interrupted (e.g., transient API error mid-destroy), stale `gcp.dns.ManagedZone` references in state trigger drift errors on subsequent `pulumi up`. | `pulumi up` re-run is idempotent — destroyed resources stay destroyed, missing creates are added, partial deletes complete. Operator re-runs `pulumi up` until clean. If a zone destroy is permanently stuck (e.g., zone has non-Pulumi-managed records that block deletion), operator manually clears non-managed records via `gcloud dns record-sets delete`, then re-runs Pulumi. |
| **R5: Cloudflare API rate limits** — Free-tier limit is 1200 API calls per 5 minutes per account. Single-apply creates ~15-20 resources per env. Well within limits, but documented for safety. | Single-apply uses one Pulumi up that batches resource creates; Pulumi internally rate-limits API calls. If hit, Pulumi retries with exponential backoff. No special handling needed. |
| **R6: Cloudflare-only public DNS = no DNS-level redundancy** — If Cloudflare DNS is fully unavailable, all public resolution fails. Cloud DNS subzones today would not survive Cloudflare's apex outage either (NS chain breaks at the apex), so this is a no-change to the SPOF reality. | Accepted. Cloudflare DNS SLA is 100% with credit. Adding a secondary DNS provider (e.g., Route53 as backup NS) is a separate hardening change post-launch, gated on observed need. |
| **R7: ACME DNS-01 CNAME flip race for api/auth (both envs) and dev web-app/backend-server/zitadel** — The new `cloudflare.DnsRecord/${name}-dns-auth-cname` reads its `name` and `content` from the existing `gcp.certificatemanager.DnsAuthorization.dnsResourceRecords` Output, not from the old `gcp.dns.RecordSet/${name}-dns-auth-cname` being destroyed. Pulumi sees no input-reference edge between destroy(old) and create(new), so they may execute in parallel. If destroy completes before create, a brief window exists where the ACME DNS-01 CNAME for the affected hostname is missing. If Google's ACME re-validation runs during this window, the Cert may transition to `DEACTIVATED`. | The Pulumi apply window for the swap is seconds; Google's ACME re-validation interval is ~24 hours per documented behavior, so the collision probability is small but non-zero. Operator post-apply step (added to tasks §10.3 / §11.2): `dig +short CNAME <google-emitted-challenge-label> @1.1.1.1` against each affected service to confirm the new CNAME resolves. If a Cert reports `state: DEACTIVATED` post-apply, recovery requires destroying + recreating the affected `DnsAuthorization` to force a fresh challenge label. The `Certificate.managed.dnsAuthorizations` field holds an input reference to the `DnsAuthorization`, so a bare `pulumi destroy --target ...DnsAuthorization` is blocked by Pulumi with `Cannot destroy resource without also destroying the following dependents`. The `--target-dependents` flag cascades through the dependent `Certificate` and `CertificateMapEntry` — but for **prod**, all three resources are `protect: true` (per D5), so each must be unprotected before the cascade succeeds. **Prod recovery procedure** (unprotect in reverse dependency order, cascade-destroy, then re-apply): `pulumi state unprotect 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/certificateMapEntry:CertificateMapEntry::${name}-cert-map-entry'`, then `pulumi state unprotect 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/certificate:Certificate::${name}-cert'`, then `pulumi state unprotect 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/dnsAuthorization:DnsAuthorization::${name}-dns-auth'`, then `pulumi destroy --target 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/dnsAuthorization:DnsAuthorization::${name}-dns-auth' --target-dependents`, then `pulumi up`. The `pulumi up` re-creates the three resources from source code, which re-applies `protect: true` automatically (state unprotect is runtime-only; source still declares `protect: true`). For **dev**, none of the three are protected, so the destroy command works directly without the unprotect steps (still use `--target-dependents` for the cascade through Certificate + CertificateMapEntry). **Note on `pulumi up --replace`**: this option does NOT bypass `protect: true` per Pulumi documentation (*"refuse to operate on any resource with protect: true that would delete it, including during a stack refresh, destroy, or **replacement**"*), so it is not a simpler alternative to the unprotect-chain procedure above. Note: the apex `web-app-*` chain is genuinely new (no race) because the apex resources never existed in prior Pulumi state for prod; that case is covered by R2. |
| **R8: Operator forgets manual Cloudflare Dashboard role lockdown** — D6 is a manual step; if skipped, the unified Cloudflare zone is editable by all team members (currently 1, but adds risk as team grows). | Tasks include the lockdown as an explicit checklist item with operator-attended status. The operator confirms completion before the prod apply trigger. |

## Migration Plan

**Phase 0 — Pre-flight (out-of-band)**

1. Confirm `pulumi up --stack prod` for `refactor-unify-env-dispatch` (cloud-provisioning PR #262) has been applied — verify via Pulumi Cloud console that prod state contains unified `Zitadel$...` URNs (not `BackendMachineKey$...` URNs). If not, **halt** — apply that first; this change depends on the unified state.
2. Confirm the prod backend Pod is healthy post-refactor-deploy (`kubectl -n backend get pods --context prod` shows `Running` 1/1).
3. Cloudflare Dashboard → Manage Account → Members: change all non-pannpers members to "Administrator Read Only" or remove. Confirm pannpers retains Super Administrator. Document the state change in the PR description.

**Phase 1 — Dev single-apply (automatic on PR merge)**

4. Open the cloud-provisioning impl PR. Pulumi preview runs automatically for both dev and prod stacks. The authoritative preview-resource breakdown lives in `tasks.md` §9.2 (dev) and §9.3 (prod) — operator reviews both previews against those expectations.
5. Pre-merge DKIM verification (dev): `dig +short TXT <selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` returns the current public key matching `pulumiConfig.postmark.dkimPublicKey` in ESC. If mismatch, **halt** — investigate before merging.
6. Merge PR. Dev `pulumi up` auto-runs via Pulumi Cloud Deployments. The apply creates the new Cloudflare resources and destroys the Cloud DNS public zone in one transaction. Note the R7 ACME CNAME flip race for the existing service Cert chains — Pulumi may execute destroy(old gcp.dns.RecordSet) and create(new cloudflare.DnsRecord) in parallel because they share no input-reference edge.
7. Verify dev: `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-dev --format='value(managed.state)'` returns `ACTIVE` (wait up to 60 min). `dig dev.liverty-music.app @1.1.1.1` returns the dev `api-gateway-static-ip` served by Cloudflare authoritative. `curl -I https://dev.liverty-music.app/` returns 200. `curl -I https://api.dev.liverty-music.app/grpc.health.v1.Health/Check` returns 200 or auth-required (not a TLS error). Postmark dashboard shows `mail.dev.liverty-music.app` sender domain verified. Per R7, also run `dig +short CNAME <google-emitted-challenge-label> @1.1.1.1` for each of `web-app`/`backend-server`/`zitadel` to confirm the new ACME CNAMEs resolve.

**Phase 2 — Prod single-apply (manual trigger)**

8. Operator triggers `pulumi up --stack prod` via Pulumi Cloud console (manual per `deployment-infrastructure` requirement). Operator reviews the preview's destroy list — especially confirming no `+- replace` on api/auth Cert resources (would indicate a `managed.domains` change that would deadlock against the existing CertMapEntry).
9. Verify prod: `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-prod --format='value(managed.state)'` returns `ACTIVE`. `curl -I https://liverty-music.app/` returns 200 (apex SPA loads). `dig +short A liverty-music.app @1.1.1.1` returns the prod `api-gateway-static-ip`. `openssl s_client -connect liverty-music.app:443 -servername liverty-music.app` shows cert issuer Google Trust Services (not Cloudflare Universal SSL). `curl -I https://api.liverty-music.app/` and `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` both return 200. Per R7, also run `dig +short CNAME <google-emitted-challenge-label> @1.1.1.1` for api and auth to confirm new ACME CNAMEs resolve.

**Rollback Strategy**

The single-apply path destroys old infrastructure in the same transaction as creating new infrastructure. Rollback options after the apply has run are limited — there is no "old state preserved as safety net" by design. Per R1/R2, failure modes during the apply are recoverable by re-running `pulumi up`; failure modes detected after the apply require active recovery, not revert.

- **If the apply itself fails mid-transaction** (transient API error, runner kill, etc.): re-run `pulumi up` for the same env. Pulumi's destroy + create is idempotent — destroyed resources stay destroyed, missing creates are added, the apply resumes from the failed step. This is the primary recovery path.
- **If the new apex Cert fails to reach ACTIVE within 60 min**: diagnose by `dig` against the Google-emitted ACME challenge label (`gcloud certificatemanager dns-authorizations describe web-app-dns-auth`). If the Cloudflare CNAME exists but Google's validator cannot resolve it, contact GCP support. Worst-case recovery: destroy + recreate the apex DnsAuthorization to force a fresh challenge label. The `web-app-cert.managed.dnsAuthorizations` input reference makes the destroy block on its dependents (`web-app-cert` + `web-app-cert-map-entry`); `--target-dependents` cascades through them, but **for prod** all three apex resources are `protect: true` (per D5), so each must be unprotected first. **Prod recovery procedure** (unprotect in reverse dependency order, cascade-destroy, then re-apply): `pulumi state unprotect 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/certificateMapEntry:CertificateMapEntry::web-app-cert-map-entry'`, then `pulumi state unprotect 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/certificate:Certificate::web-app-cert'`, then `pulumi state unprotect 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/dnsAuthorization:DnsAuthorization::web-app-dns-auth'`, then `pulumi destroy --target 'urn:pulumi:prod::liverty-music::gcp:certificatemanager/dnsAuthorization:DnsAuthorization::web-app-dns-auth' --target-dependents`, then `pulumi up`. The `pulumi up` re-creates the three resources and re-applies `protect: true` from source automatically. For dev, no protect prerequisite — destroy directly with `--target-dependents`. `pulumi up --replace` does NOT skip the unprotect step (Pulumi treats `protect: true` as blocking replacement per official docs). **Faster alternative to avoid the recovery entirely**: pre-issue the apex Cert in a preparatory PR before the main cutover (see R2 fast-path note); skipped in this change because pre-launch traffic shape makes the up-to-60-min TLS error window operationally invisible.
- **If a post-apply user-visible outage is detected on dev** (e.g., apex returns NXDOMAIN after Pulumi success): the dev Cloud DNS zone is already gone — `pulumi destroy` against the new Cloudflare records would leave the env entirely without DNS. Recovery: identify the misconfigured Pulumi resource, fix the source code, push a hotfix PR. Dev's pre-launch traffic shape makes "dev down for a few hours" tolerable.
- **If a post-apply outage is detected on prod**: same recovery path as dev — fix source, push hotfix. The `protect: true` flags on prod DNS/cert resources prevent accidental destroy; the operator can still mutate values via `pulumi up` (protect blocks destroy, not update). For an apex A record value typo, the fix lands via a one-line source change + re-apply. For a wrong cert binding, the CertMapEntry value can be updated in-place (protect does not block updates) and re-applied. For recovery paths that genuinely require destroying a protected resource (e.g., R7's DnsAuthorization re-issue), see the unprotect prerequisite documented in R7's mitigation column.
- **If both dev and prod fail in the same way**: revert the PR. The hotfix PR re-applies the change minus the bug. Note that *reverting the merge alone does not restore old Cloud DNS state* — that infrastructure is gone. The revert simply prevents further damage; positive recovery still requires running `pulumi up` against the corrected source.

## Open Questions

- **OQ1: Should the apex cert provisioning use the same `gcp.certificatemanager.Certificate` Google-managed flow, or use a Cloudflare Origin Certificate (15-year self-signed by Cloudflare, presented to clients via Cloudflare proxy)?** Recommendation: stick with Google-managed (no proxy in scope per Non-Goals; Cloudflare Origin Cert requires `proxied: true`). Revisit when Cloudflare Proxy is introduced.
- **OQ2: Should the `protect: true` annotations be applied only via `pulumi.CustomResourceOptions { protect: true }` per-resource, or by extracting a `protectInProd()` helper?** Recommendation: per-resource for explicitness — 12 occurrences is below the threshold where a helper improves readability. Reconsider if the protected-resource count grows beyond 20.
- **OQ3: Should Postmark Return-Path records be at `pm-bounces.mail` (dev) or moved to apex `pm-bounces`?** Today dev uses `pm-bounces.mail.dev.liverty-music.app`; prod uses `pm-bounces.mail.liverty-music.app`. Recommendation: keep the existing hostnames unchanged in this change; consolidating to apex is a separate Postmark-domain-config change that requires re-verifying the sender domain on Postmark side.
- **OQ4: When should Cloudflare Proxy (`proxied: true` / orange-cloud) be enabled?** Out of scope for this change. Decision point: when WAF / edge-cache value exceeds the gRPC-incompatibility cost (Connect-RPC streaming over CF Free/Pro = broken; needs Business+ plan). Document the trigger in a follow-up `enable-cloudflare-proxy` proposal.
