# Identity Management — Delta Spec

## REMOVED Requirements

### Requirement: Auto-Verify Email on Self-Registration

**Reason**: Email verification is now handled asynchronously by the backend after user creation. The `autoVerifyEmail` Zitadel Action is no longer needed because testing confirmed that the Passkey OIDC flow does NOT block on unverified email. Users are created with `email: not verified` and receive a verification email triggered by the backend via Zitadel's API.

**Migration**: Delete the `autoVerifyEmail` Action, its `PRE_CREATION` TriggerAction, and the `auto-verify-email.js` script from cloud-provisioning. No data migration is needed — existing verified users remain verified.
