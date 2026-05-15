# apex-frontend-serving Specification

## Purpose

Defines the contract for serving the apex domain `liverty-music.app` via GKE Gateway with Google-managed TLS. Cloudflare is the authoritative DNS provider, with an A record (DNS-only, `proxied: false`) pointing to the shared `api-gateway-static-ip`. All prod-stack apex resources (A record, DnsAuthorization, Certificate, CertificateMapEntry) carry Pulumi `protect: true`. Routing is handled by a pre-existing HTTPRoute (from the `prod-k8s-manifests` change) that targets the `web-app` Service in the `frontend` namespace.

## Requirements
### Requirement: Apex hostname SHALL be served end-to-end via the GKE Gateway with a Google-managed TLS certificate
The production apex hostname `liverty-music.app` SHALL serve the Aurelia frontend SPA via the same GKE Gateway that fronts `api.liverty-music.app` (backend) and `auth.liverty-music.app` (Zitadel). The apex SHALL participate in the shared Gateway / shared static IP / shared Certificate Map pattern used by the other prod hostnames. TLS termination SHALL happen at the Gateway using a Google-managed Certificate Manager certificate; Cloudflare SHALL be authoritative for the DNS A record only (Proxy OFF, no Cloudflare TLS termination).

#### Scenario: Apex A record resolves to the shared prod static IP
- **WHEN** querying `dig +short A liverty-music.app @1.1.1.1`
- **THEN** the response SHALL contain exactly the IPv4 address of the `api-gateway-static-ip` GlobalAddress in `liverty-music-prod`
- **AND** the record SHALL be served by Cloudflare authoritative nameservers (verified via `dig +trace`)

#### Scenario: Apex receives a Google-managed Certificate scoped to the single hostname
- **WHEN** inspecting the Pulumi resource graph for the prod stack
- **THEN** a `gcp.certificatemanager.Certificate` resource named `web-app-cert` SHALL exist
- **AND** its `managed.domains` SHALL equal `['liverty-music.app']` (single hostname, no SAN)
- **AND** its `managed.dnsAuthorizations` SHALL reference exactly one `gcp.certificatemanager.DnsAuthorization` resource (`web-app-dns-auth`)

#### Scenario: Apex certificate bound to the shared certificate map
- **WHEN** inspecting the `api-gateway-cert-map` resource entries
- **THEN** a `gcp.certificatemanager.CertificateMapEntry` named `web-app-cert-map-entry` SHALL exist
- **AND** its `hostname` SHALL equal `liverty-music.app`
- **AND** its `certificates` SHALL reference the `web-app-cert` resource
- **AND** the GKE Gateway listener bound to the cert map SHALL present this certificate when SNI matches `liverty-music.app`

#### Scenario: ACME DNS-01 challenge CNAME is hosted in the Cloudflare zone
- **WHEN** the `web-app-dns-auth` DnsAuthorization is created
- **AND** Google Certificate Manager emits the expected ACME challenge CNAME (label and target visible in the resource's `dnsResourceRecords` output)
- **THEN** a `cloudflare.DnsRecord` of type `CNAME` SHALL be provisioned in the `liverty-music.app` Cloudflare zone with the matching label and target
- **AND** Google's ACME validator SHALL resolve the challenge via Cloudflare's authoritative nameservers
- **AND** the Cert SHALL reach `state: ACTIVE` within 60 minutes of DnsAuthorization creation

### Requirement: Apex serving SHALL route to the `web-app` frontend Service via HTTPRoute hostname matching
The Kubernetes HTTPRoute that serves the apex SHALL match on `hostnames: ['liverty-music.app']` and route to the `web-app` Service in the `frontend` namespace. This HTTPRoute SHALL share the same Gateway as the HTTPRoutes for `api.liverty-music.app` (routing to backend) and `auth.liverty-music.app` (routing to Zitadel) — differentiation is by HTTPRoute hostname, not by Gateway listener.

> **Note**: The HTTPRoute hostname binding is pre-existing — configured by the prior `prod-k8s-manifests` change (archived 2026-05-14) in `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`. The `consolidate-public-dns-on-cloudflare` change consumes the existing binding and verifies it via a pre-flight task; it does not author or modify any HTTPRoute YAML. The requirement is documented here because the apex-frontend-serving capability collects the end-to-end serving contract regardless of which change first satisfied each piece.

#### Scenario: Frontend HTTPRoute binds apex hostname
- **WHEN** rendering `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/`
- **THEN** an `HTTPRoute` resource SHALL exist with `spec.hostnames` containing `liverty-music.app`
- **AND** the HTTPRoute SHALL reference the shared prod Gateway via `spec.parentRefs`
- **AND** the HTTPRoute SHALL route to the `web-app` Service via `spec.rules[].backendRefs`

#### Scenario: Apex traffic reaches the frontend SPA
- **WHEN** an end user requests `https://liverty-music.app/` after the prod cutover completes
- **THEN** the request SHALL receive a `200 OK` response from the Caddy-served frontend SPA
- **AND** the response body SHALL be `index.html` from the frontend container image
- **AND** the TLS certificate presented SHALL be the `web-app-cert` Google-managed certificate

### Requirement: Apex serving SHALL NOT use Cloudflare Proxy on initial deploy
The apex A record SHALL be created with `proxied: false` (Cloudflare gray-cloud / DNS-only). The Cloudflare CDN, WAF, and edge-cache features SHALL NOT terminate apex traffic on initial deploy. This decision exists to (a) match the existing pattern for `api.` and `auth.` (also Proxy OFF), (b) preserve Connect-RPC streaming compatibility (Cloudflare Free/Pro tier does not support gRPC streaming proxy; `api.` traffic would break under proxy), and (c) defer the WAF/cache benefit-vs-complexity decision to a separate future change.

#### Scenario: Apex A record is DNS-only
- **WHEN** querying the Cloudflare API for the apex A record
- **THEN** the record's `proxied` field SHALL be `false`
- **AND** no Cloudflare edge proxy SHALL intercept apex traffic

#### Scenario: Cert pinning observation
- **WHEN** running `openssl s_client -connect liverty-music.app:443 -servername liverty-music.app`
- **THEN** the certificate chain SHALL show Google Trust Services as the issuer
- **AND** the certificate SHALL NOT be a Cloudflare Universal SSL certificate
- **AND** the certificate SHALL NOT be a Cloudflare Origin certificate

### Requirement: Apex serving prod-stack resources SHALL be `protect: true`
All Pulumi resources that compose the apex serving path in the prod stack SHALL declare `protect: true` in their resource options to prevent accidental `pulumi destroy` from taking the prod apex offline.

#### Scenario: Apex A record is protect-flagged
- **WHEN** inspecting the Pulumi state for the prod-stack `cloudflare.DnsRecord` resource at the apex (`@`)
- **THEN** the resource SHALL have `protect: true`

#### Scenario: Apex cert chain is protect-flagged
- **WHEN** inspecting the Pulumi state for the prod-stack apex Certificate Manager resources
- **THEN** the `web-app-cert` Certificate SHALL have `protect: true`
- **AND** the `web-app-dns-auth` DnsAuthorization SHALL have `protect: true`
- **AND** the `web-app-cert-map-entry` CertificateMapEntry SHALL have `protect: true`

#### Scenario: Dev-stack apex-equivalent resources are NOT protect-flagged
- **WHEN** inspecting the Pulumi state for the dev-stack `cloudflare.DnsRecord` resource for `dev.liverty-music.app` (dev's apex-equivalent serving the frontend)
- **THEN** the resource SHALL NOT have `protect: true`
- **AND** dev SHALL remain destroyable for environment-rebuild scenarios

