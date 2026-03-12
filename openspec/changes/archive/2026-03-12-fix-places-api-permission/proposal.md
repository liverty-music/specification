## Why

The backend-app service account lacks the `serviceusage.services.use` permission required for OAuth-authenticated calls to Google Places API (New). When the consumer sends requests with `Authorization: Bearer` + `X-Goog-User-Project`, GCP checks that the caller has permission to use APIs on the billing project. Without `roles/serviceusage.serviceUsageConsumer`, all Places API calls return `403 permission_denied`, blocking venue enrichment.

## What Changes

- Add `roles/serviceusage.serviceUsageConsumer` to the backend-app service account's project-level IAM bindings in Pulumi (cloud-provisioning).
- This grants `serviceusage.services.use`, the minimum permission needed for OAuth + `X-Goog-User-Project` API calls.

## Capabilities

### New Capabilities

None. This is an infrastructure/IAM fix, not a new capability.

### Modified Capabilities

None. The venue enrichment capability's requirements are unchanged; this fixes a missing permission that prevents the existing implementation from working.

## Impact

- **cloud-provisioning**: `src/gcp/components/kubernetes.ts` — one IAM role addition to backend-app SA bindings.
- **backend**: No code changes. The existing Places API client will work once the IAM role is applied.
- **Deployment**: Requires `pulumi up` on the dev stack to apply the IAM binding. Effect is immediate after apply.
