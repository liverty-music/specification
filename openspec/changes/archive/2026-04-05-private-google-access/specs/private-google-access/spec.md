## ADDED Requirements

### Requirement: Private DNS zone for googleapis.com
A private Cloud DNS zone for `googleapis.com.` SHALL exist and be bound to the project VPC, resolving `*.googleapis.com` to `restricted.googleapis.com`.

#### Scenario: googleapis.com resolves via internal route
- **WHEN** a pod on a private GKE node performs a DNS lookup for any `*.googleapis.com` hostname
- **THEN** the resolved IP SHALL be within `199.36.153.4/30` (restricted.googleapis.com range)
- **AND** the lookup SHALL NOT return a public googleapis.com IP

### Requirement: Private DNS zone for restricted.googleapis.com
A private Cloud DNS zone for `restricted.googleapis.com.` SHALL exist and be bound to the project VPC, with A records for all four IPs in the `/30` range.

#### Scenario: restricted.googleapis.com A records are present
- **WHEN** querying `restricted.googleapis.com` from within the VPC
- **THEN** the response SHALL contain A records for 199.36.153.4, 199.36.153.5, 199.36.153.6, and 199.36.153.7

### Requirement: Google API traffic bypasses Cloud NAT
Google API traffic from GKE nodes SHALL route through Private Google Access and SHALL NOT be processed by the Cloud NAT gateway.

#### Scenario: No NAT processing for googleapis.com traffic
- **WHEN** a GKE pod sends a request to any `*.googleapis.com` endpoint
- **THEN** the traffic SHALL use the internal PGA route (199.36.153.4/30)
- **AND** SHALL NOT appear in Cloud NAT data processing metrics
