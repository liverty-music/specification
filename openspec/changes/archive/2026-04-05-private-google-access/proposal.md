## Why

`cluster-subnet-osaka` already has `privateIpGoogleAccess: true` in Pulumi, but without the corresponding private DNS zones for `googleapis.com`, Google API traffic still resolves to public IPs and routes through Cloud NAT — incurring $0.045/GiB data processing charges unnecessarily. Adding the DNS zones completes the Private Google Access configuration so that all `*.googleapis.com` traffic bypasses Cloud NAT entirely.

## What Changes

- **Add** a private Cloud DNS zone for `googleapis.com` resolving to `restricted.googleapis.com` (199.36.153.4/30) in `network.ts`
- **Add** a private Cloud DNS zone for `restricted.googleapis.com` with an A record pointing to 199.36.153.4–7
- No subnet change needed — `privateIpGoogleAccess: true` is already set

## Capabilities

### New Capabilities

- `private-google-access`: Private DNS configuration that routes `*.googleapis.com` traffic through Google's internal network, bypassing Cloud NAT data processing charges

### Modified Capabilities

_(none — subnet flag is already correct; only DNS is missing)_

## Impact

- **cloud-provisioning/src/gcp/components/network.ts**: Two new `gcp.dns.ManagedZone` and `gcp.dns.RecordSet` resources
- **Environments**: Applies to all environments that have private nodes (staging, prod); dev will benefit once Cloud NAT is removed by `gke-cost-optimization` only for staging/prod impact
- **Cost**: Eliminates NAT data processing charges on all Google API egress traffic for staging/prod private clusters (~unknown volume, but all logging/monitoring/trace/Gemini API calls qualify)
- **Risk**: Low — DNS change only; no workload restarts required
