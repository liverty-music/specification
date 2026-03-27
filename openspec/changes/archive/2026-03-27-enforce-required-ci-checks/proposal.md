## Why

Frontend and cloud-provisioning repositories allow merging PRs even when CI checks (lint, test) are failing. This is because their `requiredStatusCheckContexts` in Pulumi branch protection are set to empty arrays. Backend and specification already enforce `CI Success` as a required check, so there is an inconsistency across the organization.

## What Changes

- Set `requiredStatusCheckContexts: ['CI Success']` for the **frontend** repository so lint/test failures block merging.
- Set `requiredStatusCheckContexts: ['CI Success']` for the **cloud-provisioning** repository so lint failures block merging. (Pulumi preview checks cannot be required because they only appear on `src/**` changes — k8s-only PRs would be permanently blocked.)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none - this is a pure infrastructure/configuration change with no spec-level behavior impact)

## Impact

- **cloud-provisioning/src/index.ts**: Two lines changed (frontend and cloud-provisioning `requiredStatusCheckContexts` arrays).
- **Deployment**: Requires `pulumi up` on the **prod** stack, since branch protection is only applied when `environment === 'prod'`.
- **Developer workflow**: After this change, PRs to frontend and cloud-provisioning `main` branches will be blocked from merging until all required checks pass.
