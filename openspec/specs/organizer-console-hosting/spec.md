# organizer-console-hosting Specification

## Purpose
Hosting for the organizer console entry at a dedicated per-environment host,
mirroring the admin console hosting: an HTTPRoute on the shared gateway, a
TLS certificate, a Cloud DNS record, and a per-host `/config.json`.
## Requirements
### Requirement: Serve the organizer console at a dedicated per-env host

The system SHALL serve `organizer.html` at `organizer.{base-domain}` per
environment (`organizer.dev.liverty-music.app` in dev,
`organizer.liverty-music.app` in prod), provisioned via IaC: an HTTPRoute on
the shared gateway, a TLS certificate (certmap), and a Cloud DNS record. The
`organizer-console` OIDC app's redirect URIs SHALL include this host.

#### Scenario: Organizer host is reachable over TLS per environment

- **WHEN** the IaC is applied for an environment
- **THEN** `organizer.{base-domain}` for that environment SHALL resolve via
  Cloud DNS and terminate TLS via the provisioned certificate
- **AND** an HTTPRoute SHALL route it to the organizer console

### Requirement: Serve a per-host organizer config

The system SHALL serve a per-host `/config.json` for the organizer host
carrying the organizer runtime config (issuer, `organizer-console` client
id, organizer `apiBaseUrl`), with the Service Worker (if any) bypassing cache
for `/config.json`.

#### Scenario: Organizer host serves its own config

- **WHEN** the organizer console requests `/config.json` at
  `organizer.{base-domain}`
- **THEN** it SHALL receive the organizer config for that environment (not
  the consumer SPA's config)

