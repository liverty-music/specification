## Context

Private Google Access (PGA) has two required components:

1. **Subnet flag** — `privateIpGoogleAccess: true` on the subnet. Already set in `kubernetes.ts:321`.
2. **DNS resolution** — `*.googleapis.com` must resolve to the PGA IP range (`199.36.153.4/30` for `restricted.googleapis.com`), not to public IPs.

Without the DNS component, nodes with only internal IPs attempt to reach public googleapis.com IPs, which have no route from private nodes — forcing traffic through Cloud NAT. The subnet flag alone is insufficient.

Current DNS zones in `network.ts`:
- `asia-northeast2.sql.goog.` — Cloud SQL PSC (exists)
- Public zone for `*.liverty-music.app` (exists)
- **No zone for `googleapis.com` or `restricted.googleapis.com`** ← missing

Cloud NAT is configured with `sourceSubnetworkIpRangesToNat: 'ALL_SUBNETWORKS_ALL_IP_RANGES'`, meaning all egress including Google API calls currently goes through NAT.

## Goals / Non-Goals

**Goals:**
- Route all `*.googleapis.com` traffic through Google's internal network via PGA
- Eliminate NAT data processing charges on Google API traffic (Logging, Monitoring, Trace, Gemini, Secret Manager, Artifact Registry) for staging/prod
- Zero workload impact — DNS change is transparent to applications

**Non-Goals:**
- Changing the subnet flag (already correct)
- Modifying Cloud NAT source ranges (routing takes precedence automatically; NAT source range change is not required)
- Dev environment NAT savings — per GCP documentation, Private Google Access has no effect on VMs that have external IP addresses assigned. Dev nodes use `enablePrivateNodes: false` (public external IPs) so PGA provides no benefit there. Cloud NAT was also already removed from dev by `gke-cost-optimization`. The DNS zones are added to dev as well (no environment branching in the Pulumi code), but this is harmless — communication succeeds via the external IP path regardless.

## Decisions

### Decision 1: `restricted.googleapis.com` vs `private.googleapis.com`

**Chosen: `restricted.googleapis.com` (199.36.153.4/30)**

`restricted.googleapis.com` supports only Google APIs that are VPC Service Controls compatible — a stricter, more secure subset. All services used in this project (Vertex AI, Cloud Logging, Cloud Monitoring, Cloud Trace, Secret Manager, Artifact Registry) are supported.

`private.googleapis.com` (199.36.153.8/30) includes a broader set of APIs but is less restrictive. For this project, `restricted` provides the same coverage with better security posture.

### Decision 2: DNS zone structure

Two zones are required per GCP documentation:

1. **`googleapis.com.` private zone** — A wildcard CNAME record pointing `*.googleapis.com` → `restricted.googleapis.com`
2. **`restricted.googleapis.com.` private zone** — An A record with all 4 IPs in the /30 range (199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7)

Both zones must be bound to the VPC network (`vpc-osaka`).

### Decision 3: No Cloud NAT source range change needed

When a node attempts to reach `googleapis.com`, DNS resolves to `199.36.153.4/30`. VPC routing automatically uses the `restricted-googleapis` route (a default route for this range is created by GCP when PGA is enabled on the subnet) — the packet never reaches the NAT gateway. No `sourceSubnetworkIpRangesToNat` change is required.

## Risks / Trade-offs

- **API coverage gap** → If a Google API used in future is not VPC-SC compatible, it won't be reachable via `restricted.googleapis.com`. Mitigation: monitor for `CONNECTION_REFUSED` errors; switch to `private.googleapis.com` if needed.
- **DNS propagation** → New DNS zones take effect within seconds in Cloud DNS private zones. No restart required.
- **No rollback complexity** → Deleting the DNS zones reverts to previous behavior instantly.

## Migration Plan

1. Add two DNS zones and records to `network.ts` via Pulumi
2. Run `pulumi preview` to verify only DNS resources are added (no compute changes)
3. Run `pulumi up`
4. Verify: from a pod, `nslookup storage.googleapis.com` should return `199.36.153.4–7`

## Open Questions

- None.
