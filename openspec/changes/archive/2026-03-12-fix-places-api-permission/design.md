## Context

The backend consumer calls Google Places API (New) using OAuth Bearer tokens via GCP Application Default Credentials (Workload Identity). The `X-Goog-User-Project` header is set for billing attribution. GCP requires the calling service account to have `serviceusage.services.use` permission on the billing project when this header is present. The backend-app SA currently lacks this permission.

Current backend-app SA roles (in `kubernetes.ts`):
- `roles/logging.logWriter`
- `roles/monitoring.metricWriter`
- `roles/cloudtrace.agent`
- `roles/cloudsql.instanceUser`
- `roles/aiplatform.user`

## Goals / Non-Goals

**Goals:**
- Grant the backend-app SA the minimum IAM permission needed to call Places API (New) via OAuth.

**Non-Goals:**
- Changing the authentication method (e.g., switching to API key auth).
- Adding Places API-specific roles (none exist; Places API authorization is controlled by API enablement + service usage permission).
- Modifying backend application code.

## Decisions

### Use `roles/serviceusage.serviceUsageConsumer`

**Rationale:** This is the narrowest predefined role that includes `serviceusage.services.use`. It grants permission to use APIs enabled on the project, without granting ability to enable/disable APIs or manage quotas.

**Alternatives considered:**
- `roles/editor`: Includes the permission but is far too broad (violates least privilege).
- Custom IAM role: Unnecessary overhead for a single well-scoped predefined role.
- Remove `X-Goog-User-Project` header: Would break billing attribution and is required by Places API (New) for OAuth calls.

### Apply at project level (same as existing roles)

**Rationale:** The existing backend-app SA roles are all bound at the project level. This role follows the same pattern and is appropriate since the SA only operates within one project.

## Risks / Trade-offs

- **[Broader than Places API]** `serviceusage.services.use` allows calling any enabled API on the project, not just Places API. → Acceptable: the SA already has `cloud-platform` scope, and API access is further gated by API-specific IAM roles where applicable (e.g., Cloud SQL, AI Platform). Places API has no API-specific IAM role.
- **[No rollback needed]** Adding an IAM binding is non-destructive. If reverted, venue enrichment returns to the current broken state. No data loss risk.
