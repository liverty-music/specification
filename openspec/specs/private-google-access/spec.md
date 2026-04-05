# private-google-access Specification

## Purpose

Defines requirements for the Private Google Access DNS configuration that routes `*.googleapis.com` traffic through Google's internal network, bypassing Cloud NAT data processing charges for clusters with private nodes.

## Requirements

### Requirement: Private DNS zone for googleapis.com
A private Cloud DNS zone for `googleapis.com.` SHALL exist and be bound to the project VPC. The zone SHALL contain both a wildcard CNAME record (`*.googleapis.com → restricted.googleapis.com`) and an A record (`restricted.googleapis.com → 199.36.153.4/30`) in the **same zone**, enabling full intra-zone DNS resolution without cross-zone CNAME dependencies.

#### Scenario: googleapis.com resolves via internal route
- **WHEN** a pod on a private GKE node performs a DNS lookup for any `*.googleapis.com` hostname
- **THEN** the resolved IP SHALL be within `199.36.153.4/30` (restricted.googleapis.com range)
- **AND** the lookup SHALL NOT return a public googleapis.com IP

#### Scenario: restricted.googleapis.com A records are present in the googleapis.com zone
- **WHEN** querying `restricted.googleapis.com` from within the VPC
- **THEN** the response SHALL contain A records for 199.36.153.4, 199.36.153.5, 199.36.153.6, and 199.36.153.7
- **AND** these records SHALL be in the `googleapis.com.` private zone (not a separate zone)

### Requirement: Google API traffic bypasses Cloud NAT
Google API traffic from GKE nodes SHALL route through Private Google Access and SHALL NOT be processed by the Cloud NAT gateway.

#### Scenario: No NAT processing for googleapis.com traffic
- **WHEN** a GKE pod sends a request to any `*.googleapis.com` endpoint
- **THEN** the traffic SHALL use the internal PGA route (199.36.153.4/30)
- **AND** SHALL NOT appear in Cloud NAT data processing metrics
