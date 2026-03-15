## Why

Signup flow fails with `401 Unauthorized: token missing email claim`. The Zitadel `addEmailClaim` Action is supposed to inject the `email` claim into JWT access tokens, but it's unclear whether the Action is firing or failing silently. Without logging, there is no observability into Action execution on Zitadel Cloud.

## What Changes

- Add `zitadel/log` logging to the `addEmailClaim` Action script to log both successful claim injection and failure cases.
- Log the email value on success and the `user` object structure on failure for diagnostics.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a diagnostics-only change to an infrastructure script — no spec-level behavior changes.

## Impact

- **cloud-provisioning**: `src/zitadel/scripts/add-email-claim.js` — add logging via `require("zitadel/log")`
- **Zitadel Cloud**: Action script update requires `pulumi up` to deploy
- **No API, schema, or frontend changes**
