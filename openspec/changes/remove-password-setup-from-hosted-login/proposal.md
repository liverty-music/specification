## Why

Fans and Organizers' members are meant to sign in with passkeys only, and the fan hosted-login spec already says the product offers no password sign-up. Production breaks that: the hosted login's register page offers "Password" next to "Passkey" on the product org (`allowRegister=true`, local authentication on), and the authenticator choice after an invitation offers "Password" too. The public launch is near, so this entry must close before strangers can register.

Zitadel cannot express "passkeys allowed, passwords not": `allowLocalAuthentication` turns both on or off together, and turning it off leaves an empty login page (verified in production on 2026-10-13; upstream zitadel/zitadel#11682 has had no maintainer answer since then). The only place the choice can be removed is the hosted Login V2 itself.

## What Changes

- Run a patched Zitadel Login V2 image in production instead of the upstream `ghcr.io/zitadel/zitadel-login`. The patch is applied to the upstream source at the same tag as the pinned Zitadel API image (v4.20.0 today). It removes every place where a person can set a new password:
  - the Password choice and the password step of the register page;
  - the Password choice when a person picks which authenticator to set up (after an invitation or at first sign-in);
  - the set-password page (reached by a reset code or a direct URL);
  - the change-password page;
  - the password-reset request on the password page.
- Keep password **sign-in** for identities that already have a password (the automated end-to-end test fans).
- Build the patched image in `cloud-provisioning` from the upstream tag plus a patch file, push it to a new Artifact Registry repository in the production project, and point the Zitadel Helm chart's `login.image` at it. The Zitadel API image stays upstream.
- Correct the fan hosted-login spec: the end-to-end test fans with passwords also exist in production.

Out of scope, recorded as accepted risk: a person who sets a password on their own identity through the Zitadel Console's self-service pages or by calling the Zitadel API directly. Rejecting those calls with a Zitadel Actions v2 request execution is the follow-up if that risk needs closing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/hosted-login`: new requirement "The hosted login offers no way to set a password" (no password choice on sign-up or credential setup, password-setting pages not found, existing passwords still sign in); "Configure Login Policy" is modified to correct the sentence that limits password identities to the development environment.
- `components/infrastructure/organizer/web/global/hosted-login`: new requirement "The invitation flow sets up only a passkey".

## Impact

- `cloud-provisioning`: new build input (upstream tag pin + patch + GitHub Actions workflow), a new Artifact Registry repository and pull access for the cluster, and `k8s/namespaces/zitadel/overlays/prod/values.yaml` `login.image` (base and dev stay on the upstream image). Every Zitadel upgrade now also rebuilds the patched Login V2 image; a patch that no longer applies fails that build.
- Users: the register page and the invitation flow show only the passkey path. Identities without a password are unaffected otherwise; the end-to-end test fans still sign in with their passwords.
- `frontend` production E2E: `delete-my-account` signs a fresh fan up with a password on every run; it moves to signing up with a passkey from Playwright's virtual authenticator, and a new production E2E checks the hosted login pages this change closes.
- No proto or backend change.
