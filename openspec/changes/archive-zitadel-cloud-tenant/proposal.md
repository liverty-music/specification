## Why

The `self-hosted-zitadel` change cut `dev` over to an in-cluster Zitadel instance on 2026-04-30. The Zitadel Cloud tenant `dev-svijfm.us1.zitadel.cloud` was retained as a rollback target during a two-week cooldown window ending ~2026-05-14. After that window closes without major incident, the Cloud tenant is dead weight: it consumes Cloud-tier seats, holds stale OIDC clients that could be mis-targeted by a developer, and keeps `rollback to Cloud` referenced as a viable path in the design docs.

This change closes the loop: it deletes the Cloud tenant, removes the rollback escape hatch from the design docs, and codifies the absence of a Cloud fallback as a deliberate operational state rather than an accidental one.

## What Changes

- **BREAKING**: The Zitadel Cloud tenant `dev-svijfm.us1.zitadel.cloud` SHALL be deleted via the Zitadel Cloud console after the cooldown window closes clean.
- The previous OIDC client credentials minted against the Cloud tenant SHALL be considered permanently revoked (the tenant deletion already does this server-side; this change simply documents the irreversibility).
- The rollback section of `self-hosted-zitadel/design.md` (or `rollback.md` if it was extracted) SHALL be amended to remove the "revert `domain` and frontend env back to Cloud issuer" path and replace it with: "rollback now requires re-provisioning a fresh Zitadel Cloud tenant via Pulumi — multi-hour effort, not a single-revert operation."
- Any operator-facing runbook that references the Cloud issuer URL (`dev-svijfm.us1.zitadel.cloud`) SHALL be updated to remove the reference or annotate it as historical.
- No Pulumi resource is destroyed by this change. The Cloud tenant was never managed by Pulumi after the cutover (its resources were `pulumi state delete`-d during the cutover incident chain). The deletion is a manual console action, gated by a new task in this change's `tasks.md`.

## Capabilities

### Modified Capabilities

- `zitadel-self-hosted-deployment`: The "Rollback Posture" requirement (added by `self-hosted-zitadel`) SHALL be amended to drop the "Cloud tenant retained as rollback target" clause. The cooldown-window contract is fulfilled and the rollback path is now `revert PR + re-provision a fresh Cloud tenant`.

### New Capabilities

None.

### Removed Capabilities

None.

## Impact

**Affected resources**

- Zitadel Cloud tenant: `dev-svijfm.us1.zitadel.cloud` — manual delete via Zitadel Cloud console.
- `cloud-provisioning/openspec/changes/self-hosted-zitadel/design.md` (if archived already, then `cloud-provisioning/openspec/specs/zitadel-self-hosted-deployment/spec.md`): rollback section text edits only.
- Any references in `cloud-provisioning/docs/` to the Cloud-tenant issuer URL.

**Pre-conditions** (must all hold before this change applies)

- The two-week cooldown observation window (`self-hosted-zitadel` §15.2) is closed and signed off as clean.
- No open incidents reference the Cloud tenant.
- The `self-hosted-zitadel` change is archived (or in active archive).

**Reversibility**

- Tenant deletion is **irreversible** at the Zitadel Cloud level — Cloud SaaS tenants cannot be undeleted. Confirm via UI prompt; this change MUST NOT proceed if any of the pre-conditions fail.

**Out of scope**

- Staging / prod self-hosted migration (separate future change).
- Removing `@pulumiverse/zitadel` provider dependency (still used for the self-hosted instance).
