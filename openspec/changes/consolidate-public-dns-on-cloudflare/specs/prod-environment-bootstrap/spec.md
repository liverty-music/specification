## MODIFIED Requirements

### Requirement: Prod public DNS SHALL be managed entirely by Cloudflare, with apex A record bound to the shared GKE Gateway static IP
The prod project SHALL NOT provision any public Cloud DNS zone. All prod public DNS records — apex (`liverty-music.app`), `api.liverty-music.app`, `auth.liverty-music.app`, plus ACME DNS-01 challenge CNAMEs and Postmark DKIM/Return-Path records — SHALL live directly in the single Cloudflare-managed zone `liverty-music.app`. The apex SHALL have an A record pointing to the same `api-gateway-static-ip` GlobalAddress that fronts the prod GKE Gateway. The apex SHALL receive a Google-managed TLS certificate via Certificate Manager with the ACME DNS-01 challenge resolved against the Cloudflare zone.

#### Scenario: Cloud DNS hosts no prod public zones
- **WHEN** running `gcloud dns managed-zones list --project liverty-music-prod`
- **THEN** the output SHALL NOT contain any public zone for `liverty-music.app`, `api.liverty-music.app`, or `auth.liverty-music.app`
- **AND** the only zones present SHALL be the private PSC zone(s) (`asia-northeast2.sql.goog`, `private.googleapis.com`) needed for VPC-internal resolution

#### Scenario: Cloudflare zone is authoritative for all prod public hostnames
- **WHEN** running `dig +trace liverty-music.app`, `dig +trace api.liverty-music.app`, or `dig +trace auth.liverty-music.app`
- **THEN** the authoritative answer SHALL come from Cloudflare nameservers
- **AND** each query SHALL return an A record pointing to the prod `api-gateway-static-ip` IPv4 address

#### Scenario: Apex A record exists and is protected
- **WHEN** Pulumi state for the prod stack contains a `cloudflare.DnsRecord` resource with name `liverty-music.app` (`@` in the zone)
- **THEN** the record SHALL be of type `A`
- **AND** SHALL have `content` equal to the prod `api-gateway-static-ip` address
- **AND** SHALL have `proxied: false`
- **AND** SHALL declare `protect: true` in Pulumi resource options

#### Scenario: Apex certificate exists and serves TLS for the apex hostname
- **WHEN** the GKE Gateway in prod terminates HTTPS for `liverty-music.app`
- **THEN** the presented certificate SHALL be a Google-managed Certificate with `managed.domains: ['liverty-music.app']`
- **AND** the cert SHALL be bound to the shared `api-gateway-cert-map` via a `CertificateMapEntry` whose `hostname` is `liverty-music.app`
- **AND** the cert's `DnsAuthorization` ACME DNS-01 CNAME SHALL resolve via the Cloudflare zone (the CNAME record lives in Cloudflare, not Cloud DNS)

#### Scenario: Prod-stack DNS and Certificate Manager resources are Pulumi-protected
- **WHEN** inspecting the Pulumi resource graph for the prod stack
- **THEN** all `cloudflare.DnsRecord` resources for service A records (`liverty-music.app`, `api.liverty-music.app`, `auth.liverty-music.app`) SHALL declare `protect: true`
- **AND** all `gcp.certificatemanager.Certificate` resources (web-app, backend-server, zitadel) SHALL declare `protect: true`
- **AND** all `gcp.certificatemanager.DnsAuthorization` resources SHALL declare `protect: true`
- **AND** all `gcp.certificatemanager.CertificateMapEntry` resources SHALL declare `protect: true`

## REMOVED Requirements

### Requirement: Prod DNS SHALL delegate only api. and auth. subdomains to Cloud DNS, leaving the apex on Cloudflare
**Reason**: The prod public DNS architecture is consolidated entirely onto Cloudflare. The `api.liverty-music.app` and `auth.liverty-music.app` Cloud DNS subzones are destroyed; their records (A records, ACME CNAMEs) move directly into the Cloudflare apex zone. The split (apex on Cloudflare, subzones on Cloud DNS) was originally chosen under the assumption that Google Certificate Manager required Cloud DNS for DNS-01 authorization; this is empirically false ([Google docs](https://docs.cloud.google.com/certificate-manager/docs/deploy-google-managed-dns-auth) state third-party DNS providers are supported), and the asymmetry blocked apex serving because no apex A record was ever provisioned.

**Migration**: A single `pulumi up --stack prod` (operator-triggered via Pulumi Cloud console per the `deployment-infrastructure` capability) performs the transition in one transaction:

- Creates new `web-app-cert` + `web-app-dns-auth` + `web-app-cert-map-entry` for the apex (these are net-new resources because prod previously did not host an apex Cert chain). Adds the `web-app-cert-map-entry` to the shared `api-gateway-cert-map`.
- Creates new Cloudflare-direct A records for `@` (apex), `api`, `auth` labels in the `liverty-music.app` Cloudflare zone, plus the apex ACME DNS-01 CNAME in Cloudflare. The api/auth `gcp.certificatemanager.Certificate` / `DnsAuthorization` / `CertificateMapEntry` resources retain identical Pulumi URNs (their `domain` field is unchanged); only their backing ACME CNAME resource type flips from `gcp.dns.RecordSet` to `cloudflare.DnsRecord`.
- Destroys the Cloud DNS managed zones `api.liverty-music.app` and `auth.liverty-music.app`, the Cloudflare NS-delegation records that pointed to them, and the `gcp.dns.RecordSet` resources (A + ACME CNAME) that lived inside those zones.
- Pulumi's dependency graph orders the new Cloudflare CNAMEs and apex Cert to exist before the old Cloud DNS records are destroyed so the cert validators have continuous resolution.
- A ~30-second DNS propagation window may occur as resolvers transition from the cached NS-chained answer to the new Cloudflare-direct answer; this is acceptable for the pre-launch prod environment (zero real users at apply time).

The split-apply alternative (Phase A → Phase B → Phase C across two PRs) was considered and rejected — see `design.md` D3 for rationale.
