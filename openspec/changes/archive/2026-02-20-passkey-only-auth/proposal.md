## Why

The frontend OIDC configuration does not include the Zitadel org scope, causing login flows to use the Instance-level default login policy instead of the Org-level custom policy. As a result, password login is still presented even though the Org policy disables it. This change enforces passkey-only authentication by ensuring the correct org context reaches Zitadel.

## What Changes

- Add `urn:zitadel:iam:org:id:{orgId}` to the OIDC scope in `auth-service.ts` so Zitadel applies the Org-level login policy (passkey only, no password, no external IDP).
- Update the `allowExternalIdp` comment in `cloud-provisioning` to reflect the intentional passkey-only policy (remove "temporarily disabled" wording).

## Capabilities

### New Capabilities
- `passkey-only-auth`: Enforce passkey-only authentication by configuring OIDC org scope and Zitadel login policy alignment.

### Modified Capabilities
<!-- No existing specs to modify -->

## Impact

- `frontend/src/services/auth-service.ts`: OIDC scope string updated.
- `cloud-provisioning/src/zitadel/components/frontend.ts`: Comment update only (code already correct).
- Login flow behavior changes: users will no longer see a password form; only passkey prompt will appear.
