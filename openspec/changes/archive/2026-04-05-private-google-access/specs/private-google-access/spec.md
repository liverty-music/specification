## ADDED Requirements

### Requirement: Private DNS zone for googleapis.com
A private Cloud DNS zone for `googleapis.com.` SHALL exist and be bound to the project VPC, resolving `*.googleapis.com` to `restricted.googleapis.com`.

#### Scenario: googleapis.com resolves via internal route
- **WHEN** a pod on a private GKE node performs a DNS lookup for any `*.googleapis.com` hostname
- **THEN** the resolved IP SHALL be within `199.36.153.4/30` (restricted.googleapis.com range)
- **AND** the lookup SHALL NOT return a public googleapis.com IP

### ~~Requirement: Private DNS zone for restricted.googleapis.com~~
**Superseded — see tasks.md 1.3.** The original plan created a separate `restricted.googleapis.com.` private zone, but Cloud DNS private zones do not follow cross-zone CNAMEs. The A record for `restricted.googleapis.com` was placed in the same `googleapis.com.` zone instead (PR #188). The living spec at `openspec/specs/private-google-access/spec.md` reflects the correct single-zone implementation.

### Requirement: Google API traffic bypasses Cloud NAT
Google API traffic from GKE nodes SHALL route through Private Google Access and SHALL NOT be processed by the Cloud NAT gateway.

#### Scenario: No NAT processing for googleapis.com traffic
- **WHEN** a GKE pod sends a request to any `*.googleapis.com` endpoint
- **THEN** the traffic SHALL use the internal PGA route (199.36.153.4/30)
- **AND** SHALL NOT appear in Cloud NAT data processing metrics
