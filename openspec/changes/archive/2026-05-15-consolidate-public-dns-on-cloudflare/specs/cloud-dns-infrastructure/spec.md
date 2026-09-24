## MODIFIED Requirements

### Requirement: Domain Configuration via Pulumi ESC
The system SHALL accept Cloudflare configuration from Pulumi ESC environment variables, not hardcoded in code. Cloudflare zone identity is a single zone (`liverty-music.app`) authoritative for both environments — no per-env zone configuration is required.

#### Scenario: Cloudflare config passed from ESC
- **WHEN** `pulumiConfig.cloudflare.apiToken` and `pulumiConfig.cloudflare.zoneId` are set in ESC
- **THEN** the Cloudflare provider SHALL authenticate and manage zone resources for the env's stack

#### Scenario: Cloudflare config required for all envs
- **WHEN** a stack's ESC omits `pulumiConfig.cloudflare.apiToken` or `pulumiConfig.cloudflare.zoneId`
- **THEN** `pulumi preview` SHALL fail with a clear configuration error
- **AND** the stack SHALL NOT silently skip public DNS provisioning (a stack without DNS is inoperable)

### Requirement: No Manual Registrar Nameserver Update
The system SHALL NOT require manual nameserver updates at the domain registrar, as the domain is registered via Cloudflare Registrar. Cloudflare Registrar's policy ([Registrar FAQ](https://developers.cloudflare.com/registrar/faq/)) mandates that domains under its registration use Cloudflare nameservers and cannot delegate the apex to external DNS providers. Subdomain NS delegation is permitted as a workaround for external DNS at the subzone level, but this change deliberately does NOT use subdomain delegation — all public records live directly in the apex Cloudflare zone.

#### Scenario: Cloudflare Registrar nameserver constraint accepted
- **WHEN** the domain is registered via Cloudflare Registrar
- **THEN** the apex `liverty-music.app` SHALL use Cloudflare's authoritative nameservers
- **AND** no NS record SHALL exist in the Cloudflare zone delegating any subzone (e.g., `dev`, `api`, `auth`) to a non-Cloudflare DNS provider

#### Scenario: DNS resolution verified
- **WHEN** querying authoritative nameservers for `liverty-music.app`, `api.liverty-music.app`, `auth.liverty-music.app`, `dev.liverty-music.app`, `api.dev.liverty-music.app`, or `auth.dev.liverty-music.app`
- **THEN** the response SHALL come from Cloudflare nameservers (not Cloud DNS)

### Requirement: Environment Isolation via DNS Architecture
The system SHALL maintain dev/prod environment isolation through distinct A record values (each env's A records point to its own env-scoped `api-gateway-static-ip` GlobalAddress) and via Pulumi stack-state isolation of the resources that create those records. Both environments SHALL share the single authoritative Cloudflare zone `liverty-music.app`; isolation does NOT come from separate DNS providers or separate zones.

#### Scenario: Dev and prod DNS records coexist in one Cloudflare zone
- **WHEN** listing DNS records in the Cloudflare zone `liverty-music.app`
- **THEN** both dev records (with `dev.` prefix) and prod records (apex + `api.`, `auth.` prefixes) SHALL be present
- **AND** dev records SHALL resolve to the `liverty-music-dev` project's static IP
- **AND** prod records SHALL resolve to the `liverty-music-prod` project's static IP

#### Scenario: Pulumi stack-state isolation between dev and prod
- **WHEN** running `pulumi up --stack dev`
- **THEN** only the dev-stack-owned Cloudflare DnsRecord resources SHALL be created/updated/destroyed
- **AND** prod-stack-owned records (in the same Cloudflare zone, identified by Pulumi URN scoping to the prod stack) SHALL NOT be touched

#### Scenario: Single Cloudflare API token shared, scoped to one zone
- **WHEN** the Cloudflare API token is provisioned for Pulumi to use
- **THEN** the token SHALL have permissions limited to `Zone:Read` and `Zone DNS:Edit` on the `liverty-music.app` zone only
- **AND** both dev and prod stacks SHALL read the same token from a single ESC location

### Requirement: No Conflicting Private Zones
The system SHALL ensure the public Cloudflare zone does not conflict with the existing private Cloud SQL DNS zone (`asia-northeast2.sql.goog`). The Cloud SQL PSC private zone remains on Cloud DNS regardless of the public DNS consolidation, because Cloudflare has no equivalent private-zone-with-cloud-VPC-binding feature.

#### Scenario: Zones coexist
- **WHEN** the Cloudflare public zone for `liverty-music.app` is authoritative
- **AND** the Cloud DNS private zone for `asia-northeast2.sql.goog` exists in the env's GCP project
- **THEN** both zones SHALL function independently (different DNS authorities, different name scopes)
- **AND** no DNS resolution conflicts SHALL occur

## REMOVED Requirements

### Requirement: Cloud DNS Zone for Dev Environment (Subdomain Delegation)
**Reason**: Dev no longer uses a Cloud DNS subzone. The `dev.liverty-music.app` zone is destroyed and dev's DNS records move directly into the Cloudflare apex zone (with `dev` subdomain prefix on each record). This eliminates the dev/prod asymmetry where dev used Cloud DNS subzone delegation and prod used (per the now-also-removed prod-environment-bootstrap requirement) two separate Cloud DNS subzones.

**Migration**: A single `pulumi up --stack dev` (automatic on PR merge per the `deployment-infrastructure` capability) performs the transition in one transaction:

- Creates new Cloudflare-direct A records for `dev`, `api.dev`, `auth.dev` labels in the `liverty-music.app` Cloudflare zone, plus the corresponding ACME DNS-01 CNAMEs in Cloudflare. The existing `gcp.certificatemanager.Certificate` / `DnsAuthorization` / `CertificateMapEntry` resources retain identical Pulumi URNs (their `domain` field is unchanged); only the ACME CNAME backing resource type flips from `gcp.dns.RecordSet` to `cloudflare.DnsRecord`.
- Destroys the Cloud DNS managed zone `dev.liverty-music.app`, the Cloudflare NS-delegation records that pointed to it, and the `gcp.dns.RecordSet` resources (A + ACME CNAME + Postmark) that lived inside the zone.
- Pulumi's dependency graph enforces create-before-destroy *only* where an input reference exists between resources. For the dev ACME CNAME flip, the new `cloudflare.DnsRecord/${name}-dns-auth-cname` and the old `gcp.dns.RecordSet/${name}-dns-auth-cname` share a Pulumi resource *name* but differ in *type* with no inter-edge — Pulumi may execute destroy(old) and create(new) in parallel, leaving a brief gap window. See the `consolidate-public-dns-on-cloudflare` change's design.md R7 for the documented race and its mitigation (ACME re-validation interval ~24h vs Pulumi apply window of seconds; operator post-apply `dig` confirms reachability; recovery via DnsAuthorization destroy+recreate if a cert is marked DEACTIVATED).
- A ~30-second DNS propagation window may occur as resolvers transition from the cached NS-chained answer to the new Cloudflare-direct answer; this is acceptable for the pre-launch dev environment.

The split-apply alternative (Phase A → Phase B → Phase C across two PRs) was considered and rejected — see `design.md` D3 for rationale.
