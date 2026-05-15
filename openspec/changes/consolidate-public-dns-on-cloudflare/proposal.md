## Why

Visiting `https://liverty-music.app/` (prod apex) does not currently serve the application: no Cloudflare A record for the apex was ever provisioned, and no apex TLS certificate exists. The prod-environment-bootstrap design placed the apex on Cloudflare DNS-only while delegating `api.liverty-music.app` and `auth.liverty-music.app` as Cloud DNS subzones — but the follow-up to provision the apex A record was deferred (explicitly listed as a Non-Goal in `refactor-unify-env-dispatch` design.md).

Beyond the immediate apex outage, the split DNS architecture creates a permanent dev/prod asymmetry that Cloudflare Registrar's "apex NS must be Cloudflare" constraint makes impossible to clean up without consolidating on a single provider. Validated externally: Google Certificate Manager's DNS-01 authorization works with any DNS provider, so there is no remaining technical reason to keep subzones on Cloud DNS. Best practice for SaaS public DNS is single-provider (Cloudflare) + cloud DNS for private internal zones only.

## What Changes

- **BREAKING (infra)**: Destroy all three public Cloud DNS zones (`dev.liverty-music.app`, `api.liverty-music.app`, `auth.liverty-music.app`) and the Cloudflare NS-delegation records that point to them. All public DNS records (A, ACME CNAME, Postmark DKIM/Return-Path) consolidate into the single Cloudflare-managed zone `liverty-music.app`.
- **Provision apex A record + apex TLS cert** for `liverty-music.app` (prod). Apex A record points to the existing `api-gateway-static-ip` GlobalAddress. New `web-app-cert` + `web-app-dns-auth` resources provision the apex cert via Google Certificate Manager with ACME DNS-01 challenge CNAME hosted in Cloudflare.
- **Migrate dev Postmark DKIM + Return-Path records** from Cloud DNS to Cloudflare, removing the `if (environment === 'prod')` gate around the existing CF Postmark provider block.
- **Refactor `network.ts`**: delete `buildZoneTopology()` function plus `ZoneConfig` / `ZoneTopologyEntry` interfaces; rewrite `provisionManagedHostname()` to emit `cloudflare.DnsRecord` instead of `gcp.dns.RecordSet` for A + ACME CNAME records; collapse the two `cloudflare.Provider` instances (Postmark + NS delegation) into one.
- **Include apex explicitly in `SERVICES` catalog**: replace the `subdomain: null` special case (currently filtered out for prod) with an explicit empty-subdomain entry so apex receives the same cert + A record treatment as `api` / `auth`.
- **Apply `protect: true`** to prod-stack DNS A records, `gcp.certificatemanager.Certificate`, `gcp.certificatemanager.DnsAuthorization`, and `gcp.certificatemanager.CertificateMapEntry` resources. Dev resources stay destroyable.
- **Operator runbook**: Cloudflare Dashboard write permissions reduced to read-only for all members except the break-glass operator (manual prerequisite step, not Pulumi-managed in this change).

**Non-Goals** (explicit):
- Migrating the private `asia-northeast2.sql.goog` Cloud DNS zone (no Cloudflare equivalent; stays on Cloud DNS).
- Codifying Cloudflare member role assignments via `cloudflare.AccountMember` Pulumi resources (deferred to a follow-up change).
- Enabling Cloudflare Proxy (`proxied: true` / orange-cloud) for any record — all records stay DNS-only on first deploy.
- Splitting Cloudflare API tokens per environment — single shared admin token retained.
- Modifying HTTPRoute, Gateway, or Certificate Manager TLS-termination layers; they consume the new DNS/cert state without change.

## Capabilities

### New Capabilities
- `apex-frontend-serving`: Defines the end-to-end contract for serving the apex hostname `liverty-music.app` via the GKE Gateway with a Google-managed TLS certificate — covers apex A record binding to the shared static IP, apex certificate lifecycle, ACME DNS-01 challenge layout in Cloudflare, and HTTPRoute attachment to the `web-app` Service. Provides a stable spec home for future apex-related changes (Cloudflare Proxy enablement, marketing subdomain split, etc.).

### Modified Capabilities
- `cloud-dns-infrastructure`: Remove the "Cloud DNS Zone for Dev Environment (Subdomain Delegation)" requirement (dev no longer uses a Cloud DNS subzone). Modify "Environment Isolation via DNS Architecture" to declare that both dev and prod use Cloudflare exclusively for public DNS. Retain "No Conflicting Private Zones" (SQL PSC private zone coexistence) and "Cloudflare DNS Zone Management (Production)" with "Proxy OFF". Add the prod apex A record requirement.
- `prod-environment-bootstrap`: Remove the requirement "Prod DNS SHALL delegate only api. and auth. subdomains to Cloud DNS, leaving the apex on Cloudflare". Add a replacement requirement stating prod public DNS is managed entirely by Cloudflare, with `api`, `auth`, and apex records pointing to the shared `api-gateway-static-ip`.

## Impact

- **`cloud-provisioning/src/gcp/components/network.ts`**: ~150 lines deleted (`buildZoneTopology`, `ZoneConfig`, `ZoneTopologyEntry`, per-zone provisioning loop, NS delegation loop), ~80 lines modified (`provisionManagedHostname` rewrite, `SERVICES` catalog refactor), ~20 lines added (apex resources, single CF provider consolidation, `protect: true` annotations).
- **Pulumi prod state**: ~9 destroys (3 ManagedZones, 6 NS-delegation DnsRecords) + ~15 creates (apex Cert + DnsAuth + A + ACME CNAME; api/auth/apex direct Cloudflare A records) + 1 update on `api-gateway-cert-map` (adds apex entry).
- **Pulumi dev state**: ~6 destroys (1 ManagedZone, 4 NS-delegation records, 2 Postmark records) + ~10 creates (3 service A records + 3 ACME CNAMEs + 2 Postmark records directly in CF).
- **GCP Cloud DNS API cost**: Drops by 3 public zones (~¥30/month savings; negligible).
- **Cloudflare zone record count**: Increases by ~12-15 records in the single `liverty-music.app` zone (well within Free-tier limits).
- **External system**: Postmark sender domain `mail.dev.liverty-music.app` verification must be re-confirmed after dev migration (DKIM TXT and Return-Path CNAME values are identical; verification step is to confirm Postmark's revalidation succeeds).
- **Operator runbook**: Cloudflare Dashboard member roles updated out-of-band (manual prerequisite before Phase B cutover).
- **Sequencing prerequisite**: `pulumi up --stack prod` for `refactor-unify-env-dispatch` (cloud-provisioning PR #262) must be applied before this change's prod cutover — verified via Pulumi Cloud console state inspection.
