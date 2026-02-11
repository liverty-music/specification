## ADDED Requirements

### Requirement: Google-Managed Certificate Provisioning
The system SHALL obtain TLS certificates from Google Certificate Manager for the domain `api.liverty-music.app`.

#### Scenario: Certificate auto-created
- **WHEN** domain api.liverty-music.app is configured
- **THEN** Google-managed certificate is provisioned and auto-renewed before expiry

#### Scenario: Certificate is valid
- **WHEN** user visits https://api.liverty-music.app
- **THEN** certificate is signed by Google CA and valid for the domain

### Requirement: DNS Validation for Certificate Issuance
The system SHALL use DNS-based validation (via CNAME record) to prove domain ownership for certificate issuance.

#### Scenario: DNS auth challenge
- **WHEN** Certificate Manager creates DNS Authorization
- **THEN** system provides CNAME record to add to DNS provider

#### Scenario: CNAME record verified
- **WHEN** CNAME record is added to DNS and propagates
- **THEN** Certificate Manager verifies ownership and issues certificate

### Requirement: Certificate Map for Gateway Binding
The system SHALL create a Certificate Map resource that associates domain names with certificates.

#### Scenario: Certificate mapped to domain
- **WHEN** CertificateMap entry maps hostname api.liverty-music.app to api-cert
- **THEN** Gateway annotation references this map for TLS listener

#### Scenario: Multiple domains supported (future)
- **WHEN** additional domains added to Certificate Map
- **THEN** single Gateway can serve multiple domains with different certs

### Requirement: Automatic Certificate Renewal
The system SHALL automatically renew certificates before expiry without manual intervention.

#### Scenario: Certificate renewed automatically
- **WHEN** certificate is 30 days from expiry
- **THEN** Google-managed certificate auto-renews and Gateway uses new cert

### Requirement: Certificate Status Monitoring
The system SHALL provide visibility into certificate status via GCP Console and APIs.

#### Scenario: Certificate status queryable
- **WHEN** user checks Certificate Manager dashboard
- **THEN** certificate status, expiry date, and renewal history are visible

### Requirement: Zero-Downtime Certificate Update
The system SHALL apply updated certificates without terminating existing TLS connections.

#### Scenario: Certificate rotated live
- **WHEN** new certificate is issued and bound to Gateway
- **THEN** new connections use new cert, existing connections unaffected
