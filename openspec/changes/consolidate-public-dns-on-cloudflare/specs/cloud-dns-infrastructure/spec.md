## MODIFIED Requirements

### Requirement: Cloudflare DNS Zone Management (Production)
The system SHALL manage the Cloudflare DNS zone for the production domain (`liverty-music.app`) with Proxy OFF (DNS only mode). The zone SHALL be the **single authoritative source** for all public DNS records across both dev and prod environments — including A records for service hostnames, ACME DNS-01 challenge CNAMEs for Google-managed certificates, Postmark DKIM TXT records, and Postmark Return-Path CNAMEs. No public DNS subzone SHALL be delegated to Cloud DNS.

#### Scenario: Cloudflare provider configured
- **WHEN** Pulumi code in cloud-provisioning uses `@pulumi/cloudflare` package
- **THEN** Cloudflare API token and zone ID SHALL be read from Pulumi ESC (`pulumiConfig.cloudflare.apiToken`, `pulumiConfig.cloudflare.zoneId`)
- **AND** the token SHALL be shared across dev and prod stacks (no per-env split)

#### Scenario: Single Cloudflare provider instance
- **WHEN** `network.ts` instantiates `cloudflare.Provider`
- **THEN** exactly one provider resource named `cloudflare-provider` SHALL exist per stack
- **AND** no separate `postmark-cloudflare-provider` (or similar per-purpose) instance SHALL exist

#### Scenario: Proxy OFF enforced
- **WHEN** DNS records are created in the Cloudflare zone
- **THEN** all records SHALL have `proxied: false` (or the field omitted, accepting Cloudflare's default of `false` for DNS-only records)
- **AND** TLS termination SHALL remain at the GKE Gateway with Google Certificate Manager-issued certs

#### Scenario: Production A records exist for all GKE-Gateway-fronted hostnames
- **WHEN** prod public DNS is queried for `liverty-music.app`, `api.liverty-music.app`, or `auth.liverty-music.app`
- **THEN** an A record SHALL resolve to the shared `api-gateway-static-ip` GlobalAddress in the `liverty-music-prod` project
- **AND** each A record SHALL be `protect: true` in Pulumi state to prevent accidental destroy

#### Scenario: Dev A records exist for all GKE-Gateway-fronted hostnames
- **WHEN** dev public DNS is queried for `dev.liverty-music.app`, `api.dev.liverty-music.app`, or `auth.dev.liverty-music.app`
- **THEN** an A record SHALL resolve to the shared `api-gateway-static-ip` GlobalAddress in the `liverty-music-dev` project
- **AND** dev A records SHALL NOT be `protect: true` (dev must remain destroyable for environment rebuild)

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

**Migration**:
1. Phase A: Provision new Cloudflare-direct A records for `dev`, `api.dev`, `auth.dev` labels in the `liverty-music.app` Cloudflare zone, alongside the still-active Cloud DNS subzone (NS delegation continues to resolve old records). New Cloudflare ACME CNAMEs for the dev hostnames provision in parallel. Verify new dev cert reaches ACTIVE state.
2. Phase B: Destroy the Cloudflare NS-delegation records for `dev.liverty-music.app` → Cloud DNS. The Cloudflare-direct A records become authoritative. ~30 second DNS propagation window.
3. Phase C: Destroy the Cloud DNS zone `dev.liverty-music.app` and the old A records / ACME CNAMEs inside it.
