## 1. Pre-flight verification (Phase 0)

- [ ] 1.1 Confirm `pulumi up --stack prod` for `refactor-unify-env-dispatch` (cloud-provisioning PR #262) has been applied. Verify via Pulumi Cloud console (https://app.pulumi.com/pannpers/liverty-music/prod) that prod state contains `Zitadel$liverty-music` URN family (NOT `BackendMachineKey$*` URNs). If unified state not present, **halt** and apply the refactor first.
- [ ] 1.2 Confirm prod backend Pod is healthy after the refactor deploy: `kubectl -n backend get pods --context prod` shows `Running 1/1`. No `Errors.AuthNKey.NotFound` in recent logs.
- [ ] 1.3 Confirm current Cloud DNS prod zones exist as expected baseline: `gcloud dns managed-zones list --project liverty-music-prod` shows `api-liverty-music-app-public-zone` and `auth-liverty-music-app-public-zone`.
- [ ] 1.4 Confirm current Cloud DNS dev zone exists: `gcloud dns managed-zones list --project liverty-music-dev` shows `liverty-music-app-public-zone` (dev's single zone covering all 4 dev hostnames).
- [ ] 1.5 Confirm Cloudflare zone ID for `liverty-music.app` is correctly seeded in ESC at `pulumiConfig.cloudflare.zoneId` (both `liverty-music/dev` and `liverty-music/prod`). Run `esc env get liverty-music/prod pulumiConfig.cloudflare.zoneId` and verify non-empty.
- [ ] 1.6 Confirm Cloudflare API token at `pulumiConfig.cloudflare.apiToken` has `Zone:Read` + `Zone DNS:Edit` permissions scoped to `liverty-music.app` zone (Cloudflare Dashboard → My Profile → API Tokens → token details).
- [ ] 1.7 Confirm the prod frontend HTTPRoute already binds the apex hostname (pre-existing from `prod-k8s-manifests` 2026-05-14). Run `grep -n "liverty-music.app" cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`; expected output contains a line with `hostnames: ["liverty-music.app"]`. If the binding is missing, **HALT** — fix it in a follow-up PR to `cloud-provisioning` before this change's prod cutover. (Satisfies the apex-frontend-serving capability's "Frontend HTTPRoute binds apex hostname" scenario without authoring HTTPRoute YAML in this change.)

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
- [x] 4.2 In the function body: replace the `gcp.dns.RecordSet` for the A record with `new cloudflare.DnsRecord(\`\${name}-a-record\`, { zoneId: cfZoneId, name: recordName, type: 'A', content: staticIp.address, ttl: 300, proxied: false }, { parent, provider: cfProvider, protect: protectInProd })`. The `name` field is the subdomain label or `@` for apex (Cloudflare convention).
- [x] 4.3 Replace the `gcp.dns.RecordSet` for the ACME CNAME with `new cloudflare.DnsRecord(\`\${name}-dns-auth-cname\`, { zoneId: cfZoneId, name: dnsAuth.dnsResourceRecords[0].name (trailing-dot stripped), type: 'CNAME', content: dnsAuth.dnsResourceRecords[0].data (trailing-dot stripped), ttl: 300, proxied: false }, { parent, provider: cfProvider })`. ACME CNAMEs don't need protect (regenerable on cert re-issue).
- [x] 4.4 Pass `protect: protectInProd` to all three Certificate Manager resources (`DnsAuthorization`, `Certificate`, `CertificateMapEntry`) created inside the function. The caller sets `protectInProd = (environment === 'prod')`.
- [x] 4.5 Strip the Cloudflare record `name` to the subdomain part of the hostname (not the full FQDN). Implemented via `buildCloudflareRecordName(env, subdomain)` helper: dev returns `${subdomain}.dev` or `dev` for apex; prod returns `${subdomain}` or `@` for apex.

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

## 9. Pulumi preview verification (Phase A only — keeps old state)

**Important**: This change is best applied in two PRs to enable phased Phase A → Phase B+C migration. If applying in a single PR, document the rationale and accept that Phase A and B+C land together with the brief DNS gap. The recommended split:

**Implementation note (2026-05-15)**: §3-8 code refactor was applied as a **single-PR full refactor** (design.md D3 single-apply path). The §9.1 "additions only, keep old in parallel" instruction no longer applies — the refactor deletes `buildZoneTopology` + `provisionedZones` immediately. Pulumi preview will show creates AND destroys in one apply. Operator should re-read §9-11 with this context: §9.2-9.3 expected-resource lists are augmented by ~9-10 destroys (Cloud DNS zones, NS records, old Cloud-DNS-backed A records and ACME CNAMEs); §10 + §11 collapse into a single `pulumi up` per env.

- [ ] 9.1 Open Phase A PR. In `cloud-provisioning/`, push the feature branch with only the **additions** active: new Cloudflare provider config flow; new `web-app-cert` resources for apex; new `cloudflare.DnsRecord` A records and ACME CNAMEs alongside existing Cloud DNS resources. Implementation hint: temporarily keep the old `buildZoneTopology` + `provisionedZones` loop creating Cloud DNS resources, AND add the new Cloudflare-direct resources in parallel.
- [ ] 9.2 Dev preview verification (Phase A): expects ~10 creates (3 new Cloudflare A records: web-app, backend-server, zitadel; 3 new ACME CNAMEs; 1 new apex Cert + DnsAuth + CertMapEntry [but dev's "apex" = `dev.liverty-music.app` already exists as web-app — only the ACME CNAME provider changes]; 2 new Cloudflare Postmark records). Zero destroys, zero state-impacting updates.
- [ ] 9.3 Prod preview verification (Phase A): expects ~7-8 creates (1 new apex Cert `web-app-cert` + 1 new DnsAuth `web-app-dns-auth` + 1 new CertMapEntry `web-app-cert-map-entry` + 1 new apex A record + 1 new ACME CNAME for apex; new direct A records for api/auth in Cloudflare; new ACME CNAMEs for api/auth in Cloudflare). Zero destroys.
- [ ] 9.4 Operator reviews preview output and quotes the Resource Changes block in the Phase A PR description.

## 10. Phase A apply (dev → prod, manual gate between)

- [ ] 10.1 Merge Phase A PR. Dev `pulumi up` auto-runs via Pulumi Cloud Deployments.
- [ ] 10.2 **Dev Phase A verification**:
  - `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-dev --format='value(managed.state)'` returns `ACTIVE` (wait up to 60 min if not yet).
  - `gcloud certificatemanager certificates describe backend-server-cert --location global --project liverty-music-dev` shows the NEW cert is ACTIVE (it's a replacement for the old Cloud-DNS-bound cert — both may exist in this transitional state, distinguished by `dnsAuthorizations` references).
  - `dig @1.1.1.1 dev.liverty-music.app` returns the dev static IP (NS delegation still authoritative; verifies Cloudflare CAN be queried but is not yet authoritative for the A record).
- [ ] 10.3 **Prod Phase A trigger**: operator triggers `pulumi up --stack prod` from Pulumi Cloud console.
- [ ] 10.4 **Prod Phase A verification**:
  - `gcloud certificatemanager certificates describe web-app-cert --location global --project liverty-music-prod --format='value(managed.state)'` returns `ACTIVE`.
  - api/auth new certs (with Cloudflare-hosted ACME CNAMEs) are ACTIVE.
  - `dig @1.1.1.1 api.liverty-music.app` still returns the value via NS delegation chain → Cloud DNS (old authoritative path).

## 11. Phase B+C apply (cutover and cleanup, dev → prod)

- [ ] 11.1 Open Phase B+C PR. Remove from `network.ts`: the old `buildZoneTopology` + `provisionedZones` Cloud DNS provisioning loop; the old Cloud DNS-backed `gcp.dns.RecordSet` calls inside `provisionManagedHostname` (keep only the Cloudflare versions); the Cloudflare NS-delegation records for `dev.`, `api.`, `auth.` subzones. The function signature stabilizes per task 4.1.
- [ ] 11.2 Pulumi preview (Phase B+C):
  - **Dev**: expects ~7 destroys (1 ManagedZone `liverty-music-app-public-zone` + 4 NS-delegation records for `dev` subdomain + 2 dev Postmark DnsRecords in Cloud DNS — actually the Postmark in dev was in Cloud DNS; in Phase A we added them to Cloudflare; Phase B+C destroys the Cloud DNS versions; the 2-3 old A records inside the dev zone die when the zone dies); ~3 updates (CertMap reshuffles its entry references).
  - **Prod**: expects ~9 destroys (2 ManagedZones `api-liverty-music-app-public-zone`, `auth-liverty-music-app-public-zone` + 6 NS-delegation records [3 each for api + auth — assuming 3 nameservers each based on GCP's typical 3-4 NS count, adjust to observed value] + 3 old api/auth A records inside the zones). ~1 update on `api-gateway-cert-map` adding the apex entry (already added in Phase A, so this update is a no-op or absent). Zero creates.
- [ ] 11.3 **DKIM verification before dev cutover** (R3 mitigation):
  - `dig +short TXT <dkim-selector>._domainkey.mail.dev.liverty-music.app @1.1.1.1` — note the public key value (the part after `p=`).
  - Compare to `esc env get liverty-music/dev pulumiConfig.postmark.dkimPublicKey`.
  - If values match, proceed. If mismatch, **halt** — investigate ESC vs Cloudflare drift before cutover.
- [ ] 11.4 Merge Phase B+C PR. Dev `pulumi up` auto-runs.
- [ ] 11.5 **Dev cutover verification** (~30s after Pulumi up completes):
  - `dig +short dev.liverty-music.app @1.1.1.1` returns the dev static IP — answer comes from Cloudflare directly, not NS-chained to Cloud DNS.
  - `dig +short NS dev.liverty-music.app @1.1.1.1` returns empty or only Cloudflare's NS (no Google nameservers).
  - `curl -I https://dev.liverty-music.app/` returns `200 OK`.
  - `curl -I https://api.dev.liverty-music.app/grpc.health.v1.Health/Check` — depending on auth requirements, expect 200 or auth-required, but not TLS handshake failure.
  - `curl -I https://auth.dev.liverty-music.app/.well-known/openid-configuration` returns `200 OK`.
  - Postmark dev sender domain shows verified status in Postmark Dashboard.
- [ ] 11.6 **Prod cutover trigger**: operator triggers `pulumi up --stack prod` from Pulumi Cloud console.
- [ ] 11.7 **Prod cutover verification**:
  - `curl -I https://liverty-music.app/` returns `200 OK` — the apex SPA loads. **This is the primary success criterion.**
  - `dig +short A liverty-music.app @1.1.1.1` returns the prod static IP (`34.110.151.208` or current value).
  - `openssl s_client -connect liverty-music.app:443 -servername liverty-music.app < /dev/null 2>&1 | grep 'subject='` shows `CN=liverty-music.app` and issuer is Google Trust Services.
  - `curl -I https://api.liverty-music.app/` returns the backend response.
  - `curl -I https://auth.liverty-music.app/.well-known/openid-configuration` returns `200 OK` with Zitadel JSON.

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
