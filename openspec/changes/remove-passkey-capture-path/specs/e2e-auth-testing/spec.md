## REMOVED Requirements

### Requirement: Existing Passkey Capture Path Retained

**Reason**: The passkey user the requirement implicitly relies on (`pepperoni9+playwright-1@gmail.com`, a Zitadel-Cloud-era Self-Registration user) was wiped from the dev Zitadel by `self-hosted-zitadel §10`'s `truncate_users_for_zitadel_migration` Atlas migration and was never re-provisioned on self-hosted. The script (`frontend/scripts/capture-auth-state.ts`) is therefore dead code against the active dev Zitadel issuer — it opens Chromium, drives the OIDC flow to `/loginname`, and Zitadel returns "user not found". Retaining the requirement misrepresents the state of the capability.

**Migration**: Use the `Password-Based Storage State Capture Path` requirement on the same capability instead — `npm run auth:capture:password` in the `frontend` repo. The password user is Pulumi-managed on the dev Zitadel (`liverty-music/cloud-provisioning` `E2eTestUserComponent`) and the script is headless / WSL2-compatible.

If a future need for actual WebAuthn / passkey CI regression testing surfaces, that is a new design problem (Chrome DevTools virtual authenticator via `webAuthn.addVirtualAuthenticator` + Pulumi-managed device-bound enrollment) — not a fork of the deleted script's lineage. A new requirement (and likely a new component on the cloud-provisioning side) should be designed in a follow-up change.
