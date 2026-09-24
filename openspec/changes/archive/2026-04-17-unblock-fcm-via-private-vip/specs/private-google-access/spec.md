## MODIFIED Requirements

### Requirement: Private DNS zone for googleapis.com

A private Cloud DNS zone for `googleapis.com.` SHALL exist and be bound to the project VPC. The zone SHALL contain both a wildcard CNAME record (`*.googleapis.com → private.googleapis.com`) and an A record (`private.googleapis.com → 199.36.153.8/30`) in the **same zone**, enabling full intra-zone DNS resolution without cross-zone CNAME dependencies.

The system SHALL use the `private.googleapis.com` VIP rather than `restricted.googleapis.com`. Rationale: `restricted.googleapis.com` enforces a VPC Service Controls allowlist that excludes services such as Firebase Cloud Messaging; this project does not use VPC Service Controls, so the VIP-level filtering provides no security benefit and only causes 403 errors when accessing non-VPC-SC services. If VPC Service Controls is adopted in the future, the configuration MAY be switched back to the restricted VIP at that time.

#### Scenario: googleapis.com resolves via the private VIP

- **WHEN** a pod on a GKE node performs a DNS lookup for any `*.googleapis.com` hostname
- **THEN** the resolved IP SHALL be within `199.36.153.8/30` (private.googleapis.com range)
- **AND** the lookup SHALL NOT return a public googleapis.com IP
- **AND** the lookup SHALL NOT return an address in `199.36.153.4/30` (restricted VIP)

#### Scenario: private.googleapis.com A records are present in the googleapis.com zone

- **WHEN** querying `private.googleapis.com` from within the VPC
- **THEN** the response SHALL contain A records for 199.36.153.8, 199.36.153.9, 199.36.153.10, and 199.36.153.11
- **AND** these records SHALL be in the `googleapis.com.` private zone (not a separate zone)

### Requirement: Google API traffic bypasses Cloud NAT

Google API traffic from GKE nodes SHALL route through Private Google Access via the private VIP and SHALL NOT be processed by the Cloud NAT gateway.

#### Scenario: No NAT processing for googleapis.com traffic

- **WHEN** a GKE pod sends a request to any `*.googleapis.com` endpoint
- **THEN** the traffic SHALL use the internal PGA route (199.36.153.8/30)
- **AND** SHALL NOT appear in Cloud NAT data processing metrics

