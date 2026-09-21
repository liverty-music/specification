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
