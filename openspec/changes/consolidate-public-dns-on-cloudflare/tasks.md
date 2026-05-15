## 1. Pre-flight verification (Phase 0)

- [ ] 1.1 Confirm `pulumi up --stack prod` for `refactor-unify-env-dispatch` (cloud-provisioning PR #262) has been applied. Verify via Pulumi Cloud console (https://app.pulumi.com/pannpers/liverty-music/prod) that prod state contains `Zitadel$liverty-music` URN family (NOT `BackendMachineKey$*` URNs). If unified state not present, **halt** and apply the refactor first.
- [ ] 1.2 Confirm prod backend Pod is healthy after the refactor deploy: `kubectl -n backend get pods --context prod` shows `Running 1/1`. No `Errors.AuthNKey.NotFound` in recent logs.
- [ ] 1.3 Confirm current Cloud DNS prod zones exist as expected baseline: `gcloud dns managed-zones list --project liverty-music-prod` shows `api-liverty-music-app-public-zone` and `auth-liverty-music-app-public-zone`.
- [ ] 1.4 Confirm current Cloud DNS dev zone exists: `gcloud dns managed-zones list --project liverty-music-dev` shows `liverty-music-app-public-zone` (dev's single zone covering all 4 dev hostnames).
- [ ] 1.5 Confirm Cloudflare zone ID for `liverty-music.app` is correctly seeded in ESC at `pulumiConfig.cloudflare.zoneId` (both `liverty-music/dev` and `liverty-music/prod`). Run `esc env get liverty-music/prod pulumiConfig.cloudflare.zoneId` and verify non-empty.
- [ ] 1.6 Confirm Cloudflare API token at `pulumiConfig.cloudflare.apiToken` has `Zone:Read` + `Zone DNS:Edit` permissions scoped to `liverty-music.app` zone (Cloudflare Dashboard → My Profile → API Tokens → token details).
- [ ] 1.7 Confirm the prod frontend HTTPRoute structurally binds the apex hostname `liverty-music.app` (pre-existing from `prod-k8s-manifests` 2026-05-14). Run a structural check that renders the overlay and asserts the apex hostname is an exact element of `spec.hostnames` on a `kind: HTTPRoute` resource:

  ```sh
  kustomize build cloud-provisioning/k8s/namespaces/frontend/overlays/prod/ \
    | yq 'select(.kind == "HTTPRoute") | .spec.hostnames[]' \
    | grep -qx 'liverty-music.app' \
    || { echo 'HALT: apex not in HTTPRoute spec.hostnames'; exit 1; }
  ```

  A simple substring `grep` against the overlay files is **not** acceptable — it would match comments, ConfigMap values, annotations, or any unrelated occurrence of the hostname string and false-positive-pass the HALT gate. The `kustomize build | yq` chain renders the overlay, filters to `HTTPRoute` resources, extracts `spec.hostnames` as an array, and uses `grep -qx` for an exact-element match (the `-x` flag is critical: it requires the whole line to match, blocking substring false positives). If no exact match is found, **HALT** — fix it in a follow-up PR to `cloud-provisioning` before this change's prod cutover. (Satisfies the apex-frontend-serving capability's "Frontend HTTPRoute binds apex hostname" scenario without authoring HTTPRoute YAML in this change.) Prerequisites: `kustomize` and `yq` installed locally (both are standard for cloud-provisioning operators per the `Makefile lint-k8s` target).
- [ ] 1.8 (Optional, recommended for post-launch; **may be skipped pre-launch**) Lower the Cloudflare NS-delegation record TTL ahead of cutover to bound the propagation tail (design.md R1). Current NS TTL is `3600` seconds (1 h); the destructive apply may leave cached resolvers receiving `SERVFAIL` from the destroyed Cloud DNS zone for the full TTL window. Procedure: in a preparatory PR, edit `network.ts` to set `ttl: 60` on the NS-delegation Cloudflare DnsRecord entries (search for `cloudflareNsResourcePrefix` in the delegation loop in the *pre-refactor* `network.ts` state), apply via `pulumi up --stack <env>`, wait **at least 60 minutes** for the old `3600 s` cached entries to expire across resolvers, then merge the main consolidate-public-dns-on-cloudflare impl PR. **Skip condition**: for this change's pre-launch cutover, the up-to-1-hour propagation tail is operationally invisible (zero real prod users; dev tolerates the refresh-required gap), so this task may be skipped. Document the skip decision in the PR description so the audit trail records the operator's choice.

## 2. Manual prerequisite: Cloudflare Dashboard role lockdown (D6)

- [ ] 2.1 Cloudflare Dashboard → Manage Account → Members. List all members of the `liverty-music` Cloudflare account. Record current roles in PR description.
- [ ] 2.2 For each non-`pannpers` member, change role to "Administrator Read Only" (or remove if appropriate). Confirm `pannpers` retains "Super Administrator".
- [ ] 2.3 Enable Cloudflare Audit Log notifications (optional but recommended): Account Home → Audit Log → enable email alerts for any DNS record changes.
- [ ] 2.4 Document the post-lockdown member roster in the PR description. This is the operational guard for the unified Cloudflare zone going forward.

## 3. Code: refactor `network.ts` SERVICES catalog and `provisionManagedHostname`

- [x] 3.1 In `cloud-provisioning/src/gcp/components/network.ts`: change the `SERVICES` catalog type from `subdomain: string | null` to `subdomain: string`. Update the entries: `backend-server` → `subdomain: 'api'`, `web-app` → `subdomain: ''`, `zitadel` → `subdomain: 'auth'`.
- [x] 3.2 In the same file: delete the `ZoneConfig` interface, the `ZoneTopologyEntry` interface, the `buildZoneTopology()` function, and the `provisionedZones` loop. These become unreachable once subzones are gone.
- [x] 3.3 Delete the `publicZone` and `publicZoneNameservers` instance fields on `NetworkComponent` (no longer set; downstream code does not consume them per the prod path). Also delete the equivalent forwarding fields on `Gcp` in `src/gcp/index.ts`.
- [x] 3.4 Delete the `if (environment !== 'prod')` block that sets `publicZone` / `publicZoneNameservers` for non-prod envs.

## 4. Code: rewrite `provisionManagedHostname` to use Cloudflare DnsRecord

- [x] 4.1 Change `provisionManagedHostname()` signature: remove the `zone: gcp.dns.ManagedZone` arg; add `cfProvider: cloudflare.Provider`, `cfZoneId: pulumi.Input<string>`, and `protectInProd: boolean` args. Also added a `recordName: string` field on the `service` arg so the caller can pre-compute the Cloudflare-relative label.
- [x] 4.2 In the function body: replace the `gcp.dns.RecordSet` for the A record with `new cloudflare.DnsRecord(\`\${name}-a-record\`, { zoneId: cfZoneId, name: recordName, type: 'A', content: staticIp.address, ttl: 300, proxied: false }, { parent, provider: cfProvider, protect: protectInProd })`. The A record `name` field is a relative label produced by `buildCloudflareRecordName` (subdomain label, or `@` for apex). **Convention note**: this is the A-record-only convention; the ACME CNAME below uses a different form (see §4.3) because its `name` source differs.
- [x] 4.3 Replace the `gcp.dns.RecordSet` for the ACME CNAME with `new cloudflare.DnsRecord(\`\${name}-dns-auth-cname\`, { zoneId: cfZoneId, name: dnsAuth.dnsResourceRecords[0].name (trailing-dot stripped), type: 'CNAME', content: dnsAuth.dnsResourceRecords[0].data (trailing-dot stripped), ttl: 300, proxied: false }, { parent, provider: cfProvider })`. The `name` here is the FQDN form (e.g., `_acme-challenge.api.liverty-music.app`) emitted by `DnsAuthorization.dnsResourceRecords[0].name`, with only the trailing dot stripped. **Cloudflare's API accepts both relative labels and FQDNs** for the `name` field — when given a FQDN within its zone, Cloudflare normalizes by stripping the zone suffix. Passing the FQDN directly avoids extra string manipulation in the Pulumi code; this is intentional and does not violate the §4.2 A-record convention (different code path, different source value). ACME CNAMEs don't need `protect: true` (regenerable on cert re-issue).
- [x] 4.4 Pass `protect: protectInProd` to all three Certificate Manager resources (`DnsAuthorization`, `Certificate`, `CertificateMapEntry`) created inside the function. The caller sets `protectInProd = (environment === 'prod')`.
- [x] 4.5 Strip the Cloudflare record `name` to the subdomain part of the hostname (not the full FQDN) **for the A record path**. Implemented via `buildCloudflareRecordName(env, subdomain)` helper: dev returns `${subdomain}.dev` or `dev` for apex; prod returns `${subdomain}` or `@` for apex. The ACME CNAME path does not use this helper — see §4.3 for its FQDN-passthrough convention.

## 5. Code: consolidate Cloudflare provider instance (D4)

- [x] 5.1 In `network.ts`: delete the `postmark-cloudflare-provider` Provider instance (around line 161 today). Reuse the single `cloudflare-provider` instance for Postmark records.
- [x] 5.2 Move the Postmark DKIM + Return-Path record creation out of the `if (environment === 'prod')` branch — they SHALL execute for all envs. Use the dev-specific hostname `${dkimSelector}._domainkey.mail.dev` and `pm-bounces.mail.dev` when env=dev; use `${dkimSelector}._domainkey.mail` and `pm-bounces.mail` when env=prod.
- [x] 5.3 Each Postmark DnsRecord passes `provider: cloudflareProvider` (the single instance). The Postmark records do NOT get `protect: true` (Postmark verification is recoverable via dashboard re-verify if records drift).

## 6. Code: provision apex resources (D8)

- [x] 6.1 In the call site for `provisionManagedHostname` (the loop over `SERVICES`), include the `web-app` entry with empty subdomain — apex is no longer filter-excluded. For dev, this produces `web-app-a-record` at `dev` label in Cloudflare; for prod, at `@` (apex).
- [x] 6.2 Verify the apex Cert resource is named `web-app-cert` (NOT `apex-cert` or anything new — D2 naming consistency).
- [x] 6.3 Verify the apex DnsAuthorization is named `web-app-dns-auth` and the CertMapEntry is named `web-app-cert-map-entry`.

## 7. Code: clean up zone topology comments and dependsOn chains

- [x] 7.1 Update the leading comment block of section "5. Public DNS zones + Certificate Manager + shared Gateway resources" to reflect the new model: single Cloudflare zone, no Cloud DNS public zones, no NS delegation. Remove the "Dev/staging keep the original single-zone-per-env layout..." paragraph.
- [x] 7.2 The `certManagerAndDnsApis` dependsOn chain — `dns.googleapis.com` is no longer needed for the public zones (only for private PSC zones). Implementation: passed only `certManagerApi` to `provisionManagedHostname` since Cloudflare resources do not depend on `dns.googleapis.com`. The API itself stays enabled (still needed for `cloud-sql-psc-zone` and `pga-googleapis-zone` private zones).
- [x] 7.3 The `for (const { zone, services } of provisionedZones)` loop is gone (replaced by direct iteration over `SERVICES`). New iteration: `for (const svc of SERVICES) { const hostname = buildHostname(env, svc.subdomain, tld); provisionManagedHostname(...) }` where `buildHostname` and `buildCloudflareRecordName` are inline helpers.

## 8. Lint + type-check

- [x] 8.1 In `cloud-provisioning/`, run `make lint-ts` — biome + tsc must pass clean.
- [x] 8.2 `grep -rn "buildZoneTopology\|ZoneTopologyEntry\|ZoneConfig" src/` returns empty.
- [x] 8.3 `grep -rn "postmark-cloudflare-provider" src/` returns empty (consolidated into the single provider).
- [x] 8.4 `grep -rn "publicZone\|publicZoneNameservers" src/` returns empty (no consumer of these fields after their deletion).
- [x] 8.5 `grep -En "provisionManagedHostname\(" src/` shows exactly one call site (the loop in `network.ts`).

## 9. Pulumi preview verification (single-apply)

The §3-8 code refactor deletes the old Cloud DNS provisioning path in the same diff that adds the new Cloudflare records. The Pulumi preview therefore shows creates **and** destroys in a single apply per env (design D3 single-apply path). Pulumi enforces create-before-destroy ordering only where an input reference exists between resources: this holds for the new apex `web-app-*` Cert chain (genuinely new, chained via input refs) but **not** for the api/auth/web-app ACME CNAME flip (new `cloudflare.DnsRecord` and old `gcp.dns.RecordSet` share a Pulumi resource name but differ in type, with no inter-edge — see design.md R7 for the race documentation and mitigation).

- [ ] 9.1 Push the feature branch. Pulumi Cloud runs `pulumi preview` automatically for both `dev` and `prod` stacks and posts the diffs as PR comments.
- [ ] 9.2 **Dev preview expectation**: ~8 creates (3 Cloudflare A records: web-app, backend-server, zitadel; 3 Cloudflare ACME CNAMEs; 2 Cloudflare Postmark records DKIM + Return-Path) + ~13 destroys (1 ManagedZone `liverty-music-app-public-zone` + 4 NS-delegation Cloudflare records `liverty-music-app-dns-delegation-ns-{0..3}` + 6 old `gcp.dns.RecordSet` inside the dev zone [3 A + 3 ACME CNAME] + 2 dev Postmark `gcp.dns.RecordSet` resources). The dev `web-app`/`backend-server`/`zitadel` Cert chains (DnsAuthorization + Certificate + CertificateMapEntry) are **unchanged in identity** — their Pulumi URNs, `name` fields, and `domain` fields stay the same; only the backing ACME CNAME resource type flips (`gcp.dns.RecordSet` → `cloudflare.DnsRecord`). Confirm the diff matches before approving.
- [ ] 9.3 **Prod preview expectation**: ~9 creates (3 Cloudflare A records for apex/api/auth; 3 Cloudflare ACME CNAMEs; 3 new apex Cert chain resources: `web-app-dns-auth` DnsAuthorization + `web-app-cert` Certificate + `web-app-cert-map-entry` CertificateMapEntry — **all net-new per design D3 and prod-environment-bootstrap spec**, because prod never hosted an apex Cert chain before this change) + ~12 destroys (2 ManagedZones `api-liverty-music-app-public-zone`, `auth-liverty-music-app-public-zone` + 6 NS-delegation Cloudflare records [3-4 each for api + auth] + 4 old `gcp.dns.RecordSet` inside the zones [2 A + 2 ACME CNAME for api/auth]) + ~1 update on `api-gateway-cert-map` (gains apex entry). The api/auth Cert chains are unchanged in identity — only their backing ACME CNAME resource type flips. Note: exact NS-record count depends on observed GCP nameserver count (3 or 4); adjust expectation to match preview.
- [ ] 9.4 Operator reviews both preview outputs and quotes the "Resource Changes" blocks (full creates + destroys + updates) into the PR description for the review record. Verify no unexpected `+- replace` operations on the api/auth Cert resources — replaces would indicate Pulumi sees a domain-immutability change and would deadlock against the existing CertMapEntry.

## 10. Pulumi apply (dev)

Dev applies automatically on merge per the `deployment-infrastructure` capability (Pulumi Cloud Deployments). Pre-merge DKIM verification gates the merge.

- [ ] 10.1 **DKIM verification before merge** (R3 mitigation) — the gate must verify **all three** of (a) what Cloud DNS currently serves, (b) what ESC stores, and (c) what Postmark has internally recorded; agreement of only (a) and (b) would silently miss Postmark internal drift and break email verification post-apply:
  - **(a) Cloud DNS-served value**: `dig +short TXT <dkim-selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` — note the current public key value (the part after `p=`).
  - **(b) ESC value**: `esc env get liverty-music/dev pulumiConfig.postmark.dkimPublicKey` — note the stored public key.
  - **(c) Postmark internal value**: log into Postmark dashboard → Servers → sender domain `mail.dev.liverty-music.app` → verify the domain status reads **Verified** (not "Pending verification" or "Verification failed"). If Postmark shows the domain as anything other than Verified, Postmark's internally cached DKIM key has drifted from what's in Cloud DNS/ESC; re-sync via the Postmark "Verify DKIM" action before proceeding.
  - If all three agree (`dig` value matches ESC value, AND Postmark shows Verified), proceed with merge. If any of the three disagrees, **HALT** — investigate the source of drift before applying; the migration must not break Postmark's DKIM verification for dev.
- [ ] 10.2 Merge the PR. Pulumi Cloud Deployments triggers `pulumi up --stack dev` automatically.
- [ ] 10.3 **Dev verification post-apply** (~1-2 min after apply completes; cert provisioning may add up to 60 min):
  - `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-dev --format='value(managed.state)'` returns `ACTIVE`.
  - Same check for `backend-server-cert` and `zitadel-cert` — all `ACTIVE`.
  - `dig +short dev.liverty-music.app @1.1.1.1` returns the dev `api-gateway-static-ip` value, served by Cloudflare authoritative (not NS-chained to Cloud DNS).
  - `dig +short NS dev.liverty-music.app @1.1.1.1` is empty or only Cloudflare's NS (no Google nameservers remain).
  - `curl -I https://dev.liverty-music.app/` returns `200 OK`.
  - `curl -I https://api.dev.liverty-music.app/grpc.health.v1.Health/Check` returns 200 or auth-required (NOT a TLS handshake failure).
  - `curl -I https://auth.dev.liverty-music.app/.well-known/openid-configuration` returns `200 OK`.
  - Postmark dashboard for `mail.dev.liverty-music.app` sender domain shows verified status.

## 11. Pulumi apply (prod, manual trigger)

Per `deployment-infrastructure` capability, prod applies are manual via Pulumi Cloud console. Operator-attended.

- [ ] 11.1 Operator triggers `pulumi up --stack prod` from Pulumi Cloud console (https://app.pulumi.com/pannpers/liverty-music/prod/deployments). Operator approves the preview's destroy list before clicking apply.
- [ ] 11.2 **Prod verification post-apply**:
  - `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-prod --format='value(managed.state)'` returns `ACTIVE` — the apex cert is the new resource provisioned by this change.
  - `gcloud certificatemanager certificates describe backend-server-cert --location global --project liverty-music-prod --format='value(managed.state)'` returns `ACTIVE`.
  - `gcloud certificatemanager certificates describe zitadel-cert --location global --project liverty-music-prod --format='value(managed.state)'` returns `ACTIVE`.
  - `curl -I https://liverty-music.app/` returns `200 OK` — **the apex SPA loads. This is the primary success criterion for the entire change.**
  - `dig +short A liverty-music.app @1.1.1.1` returns the prod `api-gateway-static-ip` value (`34.110.151.208` or current value).
  - `openssl s_client -connect liverty-music.app:443 -servername liverty-music.app < /dev/null 2>&1 | grep -E 'subject=|issuer='` shows `CN=liverty-music.app` and issuer is Google Trust Services (NOT Cloudflare Universal SSL).
  - `curl -I https://api.liverty-music.app/` returns the backend Connect-RPC response (200 or auth-required, not TLS error).
  - `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` returns `200 OK` with Zitadel JSON.
  - `gcloud dns managed-zones list --project liverty-music-prod` no longer contains `api-liverty-music-app-public-zone` or `auth-liverty-music-app-public-zone`.

## 12. Post-cutover smoke tests

- [ ] 12.1 Browser smoke: open `https://liverty-music.app/` in a fresh browser, complete OIDC sign-in via `auth.liverty-music.app`, land in the SPA dashboard. Verify the Aurelia frontend renders without console errors.
- [ ] 12.2 Postmark smoke (dev): trigger a sign-up flow that sends a verification email from the dev backend. Email arrives within 60s.
- [ ] 12.3 Backend health smoke (prod): `kubectl -n backend logs deployment/server --context prod --tail 100` shows no recent TLS / DNS errors.
- [ ] 12.4 Cloudflare audit log review: confirm only Pulumi-attributed changes appear in the past 24 hours; no unexpected manual edits.

## 13. Documentation + archive

- [x] 13.1 Update `cloud-provisioning/docs/DEV_VS_PROD_DIFFERENCES.md` "Domain authority for `liverty-music.app` apex" and "Cloud DNS zone count" + "Certificate Manager hostnames" rows to reflect the consolidated Cloudflare model. Note that both dev and prod use Cloudflare exclusively for public DNS.
- [x] 13.2 Update `cloud-provisioning/docs/PROD_BOOTSTRAP_DECISIONS.md` if it references the "apex on Cloudflare, subzones on Cloud DNS" split. Replace with the new "single Cloudflare zone" model. (No-op: file does not reference DNS provider split — verified via `grep -E "DNS" docs/PROD_BOOTSTRAP_DECISIONS.md` returning 0 matches.)
- [x] 13.3 Run `openspec validate consolidate-public-dns-on-cloudflare --strict` in the specification repo.
- [ ] 13.4 Run `/opsx:archive consolidate-public-dns-on-cloudflare` after merging the impl PRs and verifying prod is stable for 7 days (or sooner if confident).
- [ ] 13.5 Bundle the archive PR with the impl-related spec deltas → main spec sync per memory `reference_openspec_archive_pattern.md`.
