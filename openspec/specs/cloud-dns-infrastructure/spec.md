## ADDED Requirements

### Requirement: Cloudflare DNS Zone Management (Production)
The system SHALL manage Cloudflare DNS zone for the production domain (`liverty-music.app`) with Proxy OFF (DNS only mode).

#### Scenario: Cloudflare provider configured
- **WHEN** Pulumi code in cloud-provisioning uses `@pulumi/cloudflare` package
- **THEN** Cloudflare API token and zone ID are read from Pulumi ESC (`cloudflare.apiToken`, `cloudflare.zoneId`)

#### Scenario: Proxy OFF enforced
- **WHEN** DNS records are created in Cloudflare zone
- **THEN** all records have `proxied: false` to disable CDN/proxy features
- **THEN** TLS termination remains at GKE Gateway with Certificate Manager

#### Scenario: Production A record creation
- **WHEN** static IP is reserved (Phase 1.6)
- **THEN** A record for `api.liverty-music.app` → static IP is created in Cloudflare zone
- **THEN** external load balancer can resolve the subdomain

### Requirement: Cloud DNS Zone for Dev Environment (Subdomain Delegation)
The system SHALL create a public Cloud DNS managed zone for the dev subdomain (`dev.liverty-music.app`) in GCP via subdomain delegation.

#### Scenario: Dev DNS zone provisioned
- **WHEN** Pulumi code in cloud-provisioning creates a public managed zone for `dev.liverty-music.app`
- **THEN** GCP provisions the zone with 4 Google-managed nameservers

#### Scenario: Subdomain NS record in Cloudflare
- **WHEN** Cloud DNS zone for dev subdomain is provisioned
- **WHEN** Google nameservers are output
- **THEN** NS record is created in Cloudflare zone: `dev.liverty-music.app` → Google's 4 nameservers
- **THEN** subdomain delegation is complete

#### Scenario: Dev A record creation
- **WHEN** dev static IP is reserved
- **THEN** A record for `api.dev.liverty-music.app` → dev static IP is created in Cloud DNS zone
- **THEN** dev environment uses Cloud DNS for complete isolation

### Requirement: Domain Configuration via Pulumi ESC
The system SHALL accept domain and Cloudflare configuration from Pulumi ESC environment variables, not hardcoded in code.

#### Scenario: Domain passed from ESC
- **WHEN** GcpConfig includes `domains.publicDomain` field populated from ESC (e.g., `"dev.liverty-music.app"`)
- **THEN** NetworkComponent receives domain as configuration parameter

#### Scenario: Cloudflare config passed from ESC
- **WHEN** CloudflareConfig includes `apiToken` and `zoneId` fields populated from ESC
- **THEN** Cloudflare provider authenticates and manages zone resources

#### Scenario: Config optional (dev vs. prod)
- **WHEN** GcpConfig omits domain (or domain is null)
- **THEN** NetworkComponent gracefully skips public DNS zone creation

### Requirement: No Manual Registrar Nameserver Update
The system SHALL NOT require manual nameserver updates at the domain registrar, as domain is already registered with Cloudflare.

#### Scenario: Cloudflare Registrar constraint
- **WHEN** domain is registered via Cloudflare Registrar
- **THEN** domain MUST use Cloudflare nameservers (cannot delegate root domain to external DNS)
- **THEN** subdomain delegation via NS records is the only delegation mechanism

#### Scenario: DNS propagation verified
- **WHEN** subdomain NS record is created in Cloudflare
- **THEN** user verifies with `dig NS dev.liverty-music.app` returns Google nameservers
- **THEN** dev subdomain DNS is ready for A record creation

### Requirement: Environment Isolation via DNS Architecture
The system SHALL maintain complete DNS isolation between dev and production environments.

#### Scenario: Dev environment uses Cloud DNS
- **WHEN** deployed to dev environment
- **THEN** Cloud DNS zone for `dev.liverty-music.app` is created
- **THEN** A record `api.dev.liverty-music.app` → dev static IP is managed in Cloud DNS
- **THEN** dev environment is completely isolated from production

#### Scenario: Production environment uses Cloudflare DNS
- **WHEN** deployed to production environment (future)
- **THEN** Cloudflare DNS zone for `liverty-music.app` is used
- **THEN** A record `api.liverty-music.app` → prod static IP is managed in Cloudflare
- **THEN** production uses Cloudflare DNS directly (no subdomain delegation)

#### Scenario: Multiple environment support via ESC
- **WHEN** ESC config for dev includes `gcp.domains.publicDomain: "dev.liverty-music.app"`
- **WHEN** ESC config for prod omits `gcp.domains.publicDomain` (or null)
- **THEN** prod uses Cloudflare DNS exclusively, dev uses Cloud DNS subdomain delegation

### Requirement: No Conflicting Private Zones
The system SHALL ensure the public zone does not conflict with the existing private Cloud SQL DNS zone (`asia-northeast2.sql.goog`).

#### Scenario: Zones coexist
- **WHEN** public zone for `liverty-music.app` is created
- **WHEN** private zone for `asia-northeast2.sql.goog` already exists
- **THEN** both zones function independently (different visibility settings)
- **THEN** no DNS resolution conflicts occur
