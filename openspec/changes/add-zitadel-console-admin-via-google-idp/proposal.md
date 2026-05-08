## Why

Migrating from Zitadel Cloud to self-hosted Zitadel removed the implicit
"first human admin = the person who signed up with Google" bootstrap that
Cloud provided. The current self-hosted instance has only a `pulumi-admin`
machine user, so no human can sign in to the Admin Console (`/ui/console`)
interactively. Operating IAM exclusively through a service-account JSON key
is brittle for day-to-day inspection, support, and break-glass tasks, and
it leaves no audit trail of "who is an admin" in git.

Cloud quietly used a **two-org pattern** to deliver this experience: a
personal/admin org (where the human admin lived and signed in via Google)
and a separate product org (where the application, end users, and
passkey-only login policy lived). Self-hosted bootstrap collapsed both
roles into a single `ZITADEL` org, mixing operator and product concerns and
making it impossible to add Google sign-in for admins without exposing it to
end users.

We need to (a) restore the two-org pattern as a declarative, IaC-managed
structure that bootstraps cleanly in **any** environment from day one, and
(b) add a human admin (`pannpers@pannpers.dev`) who signs in to the Console
with Google SSO and holds `IAM_OWNER` on the instance — making admin
membership reviewable via `git diff`.

## What Changes

- Adopt a **two-org structure** at the Zitadel instance level:
  - **`admin` org** — the bootstrap-time role org for operators (machine
    and human). Created by Zitadel itself when the instance is bootstrapped
    via the new configmap setting `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`.
    Hosts `pulumi-admin` (existing machine user) and the new
    `pannpers@pannpers.dev` human admin.
  - **`liverty-music` org** — the product org. Created by Pulumi via
    `zitadel.Org` and marked as the Zitadel default org. Hosts the
    `liverty-music` Project, `ApplicationOidc`, end-user `LoginPolicy`
    (passkey-only, unchanged), `login-client` machine user, and future
    end-user accounts.
- Add `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin` to
  `k8s/namespaces/zitadel/base/configmap.env` so any environment that
  bootstraps from this configmap produces an `admin` role org, no rename
  required afterwards.
- Move all currently-Pulumi-managed product resources (`Project`,
  `ApplicationOidc`, `LoginPolicy`, `login-client` MachineUser) so they
  target the new Pulumi-created `liverty-music` product org instead of the
  bootstrap admin org id constant.
- Replace the single `ZITADEL_DEV_DEFAULT_ORG_ID` constant with
  semantically-named references: a per-environment admin org id (the
  bootstrap-created org id, discovered post-bootstrap) and a Pulumi-output
  product org id.
- Provision a Google IdP at the Zitadel **instance** level so the `admin`
  org's `LoginPolicy` can list it without affecting the `liverty-music`
  org's policy. Store the Google OAuth 2.0 Client `client_id` /
  `client_secret` in Pulumi ESC.
- Pre-provision a `HumanUser` for `pannpers@pannpers.dev` in the `admin`
  org, with no initial password, email pre-verified, and an `InstanceMember`
  granting `IAM_OWNER`. On first Google sign-in, Zitadel auto-links the
  Google identity to this user by verified-email match.
- Document and codify a break-glass invariant: the `pulumi-admin` machine
  user (now in the `admin` org) and its JSON key in GCP Secret Manager
  (`zitadel-admin-sa-key`) MUST remain intact and unrotated as a recovery
  identity that does not depend on Google sign-in being operational.
- For the dev environment specifically, perform a one-time Zitadel database
  wipe + re-bootstrap to apply the new configmap. End-user data is empty,
  so the wipe has no user-visible cost. Frontend OIDC `client_id` will
  change as a result; Pulumi rewires the new value automatically through
  ESC.

Scope: **dev only** in this change. Staging / prod use the same configmap
+ Pulumi pattern from their first bootstrap, no rename or wipe required.

## Capabilities

### New Capabilities

_None._ All requirements added by this change extend the existing
`identity-management` capability.

### Modified Capabilities

- `identity-management`: Restructures the instance into a two-org topology
  (`admin` role org + `liverty-music` product org). The existing
  organization / project / OIDC application / login-policy requirements are
  re-scoped to the new `liverty-music` product org. Adds requirements for
  the bootstrap-time `admin` role org, an instance-level Google IdP, a
  human admin user with `IAM_OWNER`, IdP auto-linking by verified email,
  break-glass machine-user retention, and Google OAuth client provisioning.

## Impact

- **Affected repos**:
  - `cloud-provisioning`:
    - `k8s/namespaces/zitadel/base/configmap.env` — add
      `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`.
    - `src/zitadel/constants.ts` — replace `ZITADEL_DEV_DEFAULT_ORG_ID`
      with admin / product split and per-env mapping.
    - `src/zitadel/index.ts` and components — wire new `liverty-music`
      product org, IdP, HumanUser, InstanceMember resources.
    - Pulumi ESC `liverty-music/cloud-provisioning/dev` — new keys for
      Google OAuth client.
  - `specification` — this OpenSpec change.
- **External dependency**: A Google Cloud OAuth 2.0 Web Application client
  must exist in the `liverty-music-dev` GCP project under the `pannpers.dev`
  Workspace, with Authorized redirect URI pointing at the Zitadel Login V2
  IdP callback path (exact path confirmed during implementation).
- **One-time dev migration**: Drop the dev Zitadel database in Cloud SQL,
  restart the Zitadel pod so the new configmap re-bootstraps the instance.
  Acceptable because the dev instance has no human end users yet
  (post-cutover). Re-bootstrap regenerates `pulumi-admin`'s SA key, which
  the existing bootstrap-uploader sidecar uploads to GCP Secret Manager
  idempotently.
- **Frontend OIDC `client_id` rotation**: After re-bootstrap and Pulumi
  apply, the `liverty-music` Project's `ApplicationOidc` will have a new
  `client_id`. Pulumi already wires this through ESC into the frontend
  config, so no manual frontend code change is required — only a Pulumi
  apply on the frontend stack.
- **Break-glass invariant**: `pulumi-admin` machine user and its JSON key
  in GCP Secret Manager (`zitadel-admin-sa-key`) remain intact across this
  change. The bootstrap-uploader sidecar's idempotent re-upload is the only
  expected key write.
- **No proto changes, no BSR release, no backend changes** required.
