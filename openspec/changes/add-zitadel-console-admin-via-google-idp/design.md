## Context

The self-hosted Zitadel v4.13.1 instance is reachable at
`https://auth.dev.liverty-music.app`. Live API inspection
(`POST /admin/v1/orgs/_search` against the existing instance with the
`pulumi-admin` JWT key) confirms the current state is **a single org**:

```
id   = 369968599999251129
name = "ZITADEL"               (Zitadel's bootstrap default — configmap
                                does not set ZITADEL_FIRSTINSTANCE_ORG_NAME)
domain = zitadel.auth.dev.liverty-music.app
```

This single org currently holds *every* Pulumi-managed resource: the
`liverty-music` Project, the frontend `ApplicationOidc`, the passkey-only
`LoginPolicy`, the `pulumi-admin` machine user (created by Zitadel
bootstrap), the `login-client` machine user (Login V2 PAT), plus any future
end-user accounts. End-user identity for the `liverty-music` SaaS is
governed by the existing `identity-management` capability, which mandates
this org's `LoginPolicy` enforces `PasswordlessType=ALLOWED`,
`UserLogin=false`, `AllowExternalIdp=false`.

For comparison, the prior Zitadel Cloud instance ran a **two-org topology**
(verified from a Cloud Console screenshot supplied during exploration):

```
Org "pannpers"      (created at sign-up; held the human admin + Google IdP)
Org "liverty-music" (default; held Project / ApplicationOidc / end users)
```

Cloud achieved "admin signs in via Google, end users sign in via passkey"
by giving each role its own org (and therefore its own login policy).
Self-hosted bootstrap collapsed both roles into one org, which is the root
cause of the current admin-Console-access gap.

The self-hosted instance has **no human end users yet** (post-cutover from
Cloud, no migration of fan accounts has happened). This unlocks an option
that would otherwise be invasive: re-bootstrap the dev instance with a
corrected configmap so the bootstrap-created org is named `admin` from the
start, then create the `liverty-music` product org via Pulumi.

## Goals / Non-Goals

**Goals:**

- Replicate Cloud's two-org pattern as a declarative, IaC-managed structure
  that any environment (dev, staging, prod) can bootstrap into directly,
  with no rename / migration step required at first install.
- `pannpers@pannpers.dev` can open
  `https://auth.dev.liverty-music.app/ui/console`, click "Sign in with
  Google", and land in the Console as `IAM_OWNER`.
- The end-user `liverty-music` org's passkey-only policy is unchanged in
  spirit — re-created cleanly under the new product org with the same
  semantics.
- All admin-identity setup (org, IdP, user, role grant) is declared in
  Pulumi — no manual Console clicks to bootstrap the next admin.
- A documented break-glass identity (`pulumi-admin` machine user + JSON
  key) survives the change and can recover Console access if Google SSO
  breaks.

**Non-Goals:**

- Adding additional human admins beyond `pannpers@pannpers.dev` in this
  change (next admin = one extra `HumanUser` resource in the same `admin`
  org, future change).
- Customising Login V2 branding (covered by separate change
  `customize-zitadel-auth-ui`).
- Rolling this out to staging or prod (separate change after dev soak).
  Both will use the same configmap + Pulumi pattern, with a fresh bootstrap.
- Replacing `pulumi-admin` machine user — it stays in the `admin` org for
  IaC and break-glass.
- Federated SSO via Google Workspace SAML / SCIM provisioning. Generic
  Google OAuth IdP is sufficient for a small admin team and matches
  Zitadel Cloud's default sign-in experience.

## Decisions

### D1: Two-org topology — `admin` (role org) + `liverty-music` (product org)

**Choice:** Split the instance into two orgs by responsibility:

- **`admin`** — Bootstrap-created. Holds operator identities only:
  `pulumi-admin` (machine, IaC + break-glass), `login-client` machine user
  (existing PAT host — see D7), `pannpers@pannpers.dev` (human, Google
  SSO). Login policy permits external IdP.
- **`liverty-music`** — Pulumi-created, marked Zitadel default. Holds
  product resources and end-user identities only: `liverty-music` Project,
  frontend `ApplicationOidc`, passkey-only `LoginPolicy`, future fan
  accounts.

**Why:**

- Zitadel `LoginPolicy` is per-org. Two policies → two orgs. There is no
  per-app, per-user, or per-role policy mechanism that lets one org expose
  Google to admins while hiding it from end users.
- Mirrors Cloud's working pattern, so operators with Cloud muscle memory
  recognise the topology.
- Adding admins later is a single `HumanUser` + `InstanceMember` pair in
  the `admin` org — no IdP, OAuth client, or Console URL change needed.
- Adding future products (e.g., a separate concert-organiser dashboard) is
  a single `zitadel.Org` plus its own Project / ApplicationOidc — no
  conflict with admin or with the existing product.

**Alternatives considered:**

- *Single org, relax existing passkey-only requirement*: simplest, but
  permanently exposes a "Sign in with Google" button to fans. Rejected
  because the existing capability owner explicitly chose passkey-only and
  no product-side reconsideration is happening in this change.
- *Single org with email-domain-based routing*: would require Login V2 to
  re-render IdPs after the user types an email. Brittle (depends on
  unverified Zitadel routing semantics in v4) and gives the admin a
  two-step login UX vs the existing one-step.
- *Rename existing org "ZITADEL" → "liverty-music" + add new admin org*:
  conceptually backwards (the bootstrap org should keep its operator role,
  not be repurposed for product). Also leaves the configmap silent on the
  bootstrap org's name, hiding intent.

### D2: Naming — role org is `admin`, not `pannpers` or `console`

**Choice:** The role org is called `admin`.

**Why:**

- *Not `pannpers`*: Cloud's per-person org naming is a SaaS sign-up
  artifact, not a deliberate product decision. Self-hosted has no reason
  to put a person's name on an org. Future admins would each need their
  own org under that scheme — extra orgs, duplicated IdP setup, more spec
  to write.
- *Not `console`*: Console is one tool that uses this org's policy, but it
  is not the only conceivable admin tool (CLI, direct API, future
  internal dashboards). Naming the org after a tool ages poorly,
  especially given Zitadel v4's direction of de-emphasising the legacy
  Console UI.
- *`admin` is role-based*: matches the IaC convention (e.g., AWS
  Organizations "Admin" OU, Google Cloud `admin` folder) and is what a
  reader expects to see.

### D3: Strategy — "configmap-bootstrapped role org + Pulumi-created product org" (strategy Z)

**Choice:** Add `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin` to
`k8s/namespaces/zitadel/base/configmap.env` so that **every** environment's
first-instance bootstrap creates the role org with the correct name,
without needing Pulumi to rename it afterwards. Pulumi then creates the
`liverty-music` product org via `zitadel.Org`.

For dev, where bootstrap has already run with the wrong configmap, perform
a one-time database wipe to force re-bootstrap with the new configmap.
There are no human end users to lose.

**Why:**

- IaC honesty: the configmap declares the bootstrap org's name. There is
  no Pulumi-managed override hiding the truth.
- Environment parity: dev, staging, and prod all bootstrap into the same
  end state through the same code path. Prod gets the correct name on its
  very first install — no rename trick to remember a year from now.
- Separation of concerns: Zitadel bootstrap owns the `admin` org (because
  it must, to hold the bootstrap-created `pulumi-admin` machine user that
  Pulumi authenticates as). Pulumi owns the `liverty-music` product org
  and everything inside it (because product evolution belongs in IaC).

**Alternatives considered:**

- *Strategy X (rename)*: smaller dev diff (no DB wipe, no `client_id`
  rotation), but leaves a permanent "rename" fingerprint that prod also
  has to perform on first install. Hides intent in Pulumi instead of
  declaring it in configmap. Rejected for honesty / parity reasons.
- *Pulumi creates the bootstrap org too*: chicken-and-egg — Pulumi
  authenticates as `pulumi-admin`, which lives in the bootstrap org, which
  Pulumi cannot create without already being authenticated. Bootstrap
  must own at least the role org.

### D4: Place Google IdP at the **instance** level

**Choice:** Use `@pulumiverse/zitadel.IdpGoogle` (instance-scoped), not
`OrgIdpGoogle`.

**Why:** An instance-level IdP is referenceable by any org's `LoginPolicy`.
The `admin` org's policy lists it; the `liverty-music` org's policy does
not. The same IdP can be reused if a future product org also wants Google
sign-in for its admins.

### D5: Pre-create the human admin, then pre-link the Google identity

**Choice:** Pulumi creates a `HumanUser` in the `admin` org with
`email = pannpers@pannpers.dev`, a Pulumi-generated random
`initialPassword`, and `isEmailVerified = true`. Pulumi then declares
a `ZitadelUserIdpLink` Dynamic Resource (see D11) that pre-creates
the binding between the admin Google IdP and that local user, keyed
by the admin's Google OIDC `sub` claim. First Google sign-in resolves
directly to the local user via the pre-existing `(idpId, sub)`
record — no email match, no UI prompt.

**Why the random password is required and harmless:** the
`@pulumiverse/zitadel` `HumanUser` resource documents that
`isEmailVerified` can only be set to `true` at creation time when the
user also has a password set. Without `isEmailVerified = true` the OIDC
sign-in flow would force an OTP step (existing pattern documented in the
"Auto-Verify Email on Self-Registration" requirement of the
identity-management capability). The password is unreachable in practice
because the `admin` org's `LoginPolicy.userLogin = false` disables the
username + password sign-in form altogether — the Login V2 UI for the
`admin` org only ever presents the IdP buttons.

**Why pre-link instead of email auto-link** (the path originally
considered here, before smoke-testing PR #228 surfaced the gap): see
D11. Briefly — the `admin` org's policy combination
(`userLogin = false` + `isCreationAllowed = false`) disables every
native first-sign-in path Zitadel offers, so the link record must
exist *before* the first sign-in arrives.

**Alternative considered:** Use the `setEmailVerified` Action pattern
(post-creation API call, mirroring the existing self-registration
auto-verify Action) to avoid setting any password. Rejected as more
complex than a random password the policy disables; the Action approach
is justified for end-user self-registration but adds no value for a
single Pulumi-provisioned admin.

### D6: Place the Google OAuth 2.0 Client in `liverty-music-dev` GCP project — manually, one-time

**Choice:** Provision the OAuth 2.0 Web Application client in the
`liverty-music-dev` project alongside the GKE cluster, Cloud SQL, and
Zitadel workload. Capture `client_id` / `client_secret` and write to ESC
`liverty-music/cloud-provisioning/dev` under
`pulumiConfig.zitadel.googleAdminIdp.clientId` /
`.clientSecret` (encrypted). Pulumi reads from ESC and configures the
Zitadel `IdpGoogle` resource.

**Why the client is manual, not Pulumi-managed:** Google has never
exposed a public API for creating general-purpose OAuth 2.0 Web
Application clients programmatically. The only declarative-tool option
in the current `@pulumi/gcp` provider is `gcp.iap.Client`, which:
(1) is deprecated as of 2025-01-22 and shut down 2026-03-19 (the IAP
OAuth Admin APIs are gone), and (2) is scoped to Identity-Aware Proxy,
not general OIDC sign-in flows — wrong shape for Zitadel's use as an
external IdP. The Google Cloud Console is the only canonical creation
path.

**Why this is acceptable:** OAuth client creation is a true one-time
event per environment. The consent screen is "Internal" (limited to the
`pannpers.dev` Workspace), so no Google review or external verification
is required. After creation, all changes (redirect URI updates, secret
rotation) happen via the Console + ESC + `pulumi up`. The client's
existence and redirect URI are documented in the cloud-provisioning
runbook so a deleted client can be recreated identically.

**Why dev project, not a separate identity-only project:** keeps all
dev infra in one project for billing / IAM clarity. The dev cluster's
Workload Identity already trusts secrets from this project's Secret
Manager. Avoids a new "identity-only" GCP project for a single OAuth
client.

### D7: `login-client` machine user belongs in the `admin` org

**Choice:** Move the existing `login-client` machine user (Login V2 PAT
host) from the current bootstrap org to the new `admin` org.

**Why:** `login-client` is operator infrastructure (the Login V2 service
authenticates Zitadel API calls with this PAT). It is not a product
identity. Keeping it in `admin` keeps the rule "the `liverty-music` org
contains only product-relevant identities" clean.

After re-bootstrap, Pulumi recreates `login-client` in the `admin` org.
The k8s `ExternalSecret` that consumes its PAT does not change — only the
underlying Pulumi `MachineUser`'s parent org changes.

### D8: Console login routing — admin org MUST be the Zitadel default org

**Choice:** The Zitadel `admin` role org is marked `isDefault: true`;
the `liverty-music` product org is marked `isDefault: false`. The admin
org is brought into Pulumi state via a one-time
`pulumi import zitadel:index/org:Org admin <admin-org-id>` (run with
`--provider liverty-music-provider=...`) and protected with
`{ protect: true }` because `pulumi destroy` against it would also
remove the bootstrap-created `pulumi-admin` machine user that the
provider authenticates as.

**Why (empirically established post-implementation):** Smoke-testing the
first deploy (`https://auth.dev.liverty-music.app/ui/console` against
the merged PRs #225/226/227) revealed that **Login V2 uses the default
org's *own* `LoginPolicy`** when the incoming OIDC AuthN omits an
`org_id` parameter — which the Zitadel-internal Console always does.
The three hypotheses originally listed in this section
(DefaultLoginPolicy fallback / user-home-org / email-domain) are all
wrong; only "default org policy" matched observed behaviour.

When `liverty-music` was the default org, Console hit the product-org
policy (passkey + register, no IdP buttons) and the admin's "Sign in
with Google" button never appeared. After flipping `isDefault` to the
admin org, Console hits the admin-org policy (Google IdP enabled,
`userLogin = false`) — the intended path.

End-user OIDC traffic from the frontend SPA is unaffected by the
default-org flip: the SPA's `ApplicationOidc` carries its own
`client_id` and Zitadel resolves that to the owning org
(`liverty-music`) regardless of default status. So the routing rule is
asymmetric:

- Console (no `client_id` known to Zitadel as application of an org) →
  default org's policy → must point at `admin`.
- Frontend SPA (explicit `client_id` for `web-frontend` in
  `liverty-music` Project) → owning org's policy → unaffected by
  default-org choice.

The IAM-level `DefaultLoginPolicy` resource is still configured with
the same Google IdP + `userLogin = false` shape as the admin org policy
as a defence-in-depth for any org that does not declare its own
`LoginPolicy`. It is not the active policy for Console login on this
instance, but keeping the two in sync makes accidental misconfiguration
of either one less catastrophic.

**Operational note:** the admin org `protect: true` flag enforces that
removing it requires an explicit code change in a reviewable PR before
any `pulumi destroy` can take effect. Without that protection, a
careless destroy would cascade into `pulumi-admin`, the
`zitadel-admin-sa-key` GSM secret would no longer match any user in
Zitadel, and the provider would stop being able to authenticate — a
hard lockout that only `kubectl rollout restart` of the Zitadel pod (to
re-bootstrap with a fresh first-instance) could recover from.

### D9: Frontend OIDC `client_id` rotation is acceptable

**Choice:** Accept that the frontend SPA's OIDC `client_id` will change
when Pulumi recreates `ApplicationOidc` inside the new `liverty-music`
product org. Pulumi already wires the `client_id` through ESC into the
frontend stack, so the rotation propagates automatically on the next
frontend Pulumi apply.

**Why:** Avoids manual frontend code changes. Zitadel does not support
"importing" an existing `ApplicationOidc` into a new org while preserving
the `client_id`, so a new id is unavoidable; the question is only whether
the frontend handles it cleanly. ESC-driven config means it does.

### D10: Retain `pulumi-admin` machine user as break-glass identity

**Choice:** The `pulumi-admin` machine user (now in the `admin` org after
re-bootstrap) and its JSON key in GCP Secret Manager
(`zitadel-admin-sa-key`) MUST remain intact. They serve as a recovery
identity that does not depend on Google sign-in.

**Why:** Two independent failure modes (Pulumi/IaC vs Google SSO) keep us
out of total-lockout scenarios. Pulumi can be re-authenticated with the
SA key from any operator's machine to restore the human admin, the IdP,
or the login policy if any of them break.

The bootstrap-uploader sidecar's idempotent re-upload pattern in
`deployment-api.yaml` means re-bootstrap regenerates the SA key (it is the
*new* `pulumi-admin`'s key, since the org and user are recreated) and the
sidecar uploads the new value. The Pulumi `@pulumiverse/zitadel` provider
reads the latest GSM version and continues to authenticate.

### D11: Pre-link Google identity via `ZitadelUserIdpLink` Dynamic Resource

**Context:** Established empirically after PR #228 merged. With the
admin org as Zitadel default (D8) and the Google IdP wired correctly
(D4), the Console UI rendered the Google sign-in button — but the
first Google sign-in dead-ended on
`/ui/v2/login/idp/google/account-not-found`. Login V2 saw an
unrecognised external identity and had no native path to attach it
to the pre-provisioned `pannpers` local user.

**Choice:** Pulumi declares a `ZitadelUserIdpLink` Dynamic Resource
(`src/zitadel/dynamic/user-idp-link.ts` in cloud-provisioning) that
calls Zitadel's v2 user service
`POST /v2/users/{userId}/links` at IaC time, with body:

```json
{
  "idpLink": {
    "idpId": "<zitadel admin Google IdP id>",
    "userId": "<google sub claim>",
    "userName": "<email or display label>"
  }
}
```

The admin's Google `sub` claim is provisioned via ESC
`pulumiConfig.zitadel.adminGoogleSubs.<userName>` and threaded through
`HumanAdminComponent`. With the link record already present, the IdP
callback resolves directly to the local user and Console loads.

**Why the `admin` org's policy combination forces this:** Zitadel
offers exactly two native first-sign-in paths to attach an external
identity to a Zitadel user, and the `admin` org's policy disables
both:

1. **autoLink prompt** (`isLinkingAllowed = true` on the IdP) — Login V2
   shows a "to link this Google account, sign in with your existing
   Zitadel account" form. Requires the existing local user to have a
   working sign-in path. The admin org's `LoginPolicy.userLogin = false`
   disables the username + password form, so the prompt has nothing to
   authenticate against. Confirmed empirically: the prompt page shows
   no input fields when userLogin is false.
2. **auto-creation** (`isCreationAllowed = true` + `isAutoCreation = true`
   on the IdP) — Zitadel mints a fresh local user from the Google
   profile without a prompt. Disabled in our setup because **anyone**
   in the `pannpers.dev` Workspace would silently become an
   instance-level Zitadel user, and a follow-up Action would still need
   to grant `IAM_OWNER`. Adds attack surface for no operational benefit
   over pre-linking.

Pre-linking sidesteps both prompts. The link record is just a database
row keyed by `(idpId, externalUserId)`, and Zitadel happily accepts
that the external identity is "already known" when the OAuth callback
arrives.

**Why a Dynamic Resource (not `@pulumiverse/zitadel`):**
`@pulumiverse/zitadel` v0.2.0 exposes neither a `UserIdpLink` resource
nor the `auto_linking: AUTO_LINKING_OPTION_EMAIL` option that the
official Zitadel Terraform provider has on its IdP resources (which,
even if it existed in our provider, would still trigger the autoLink
prompt and dead-end on `userLogin = false`). The Dynamic Resource
pattern is already used in this repo for `smtp-activation` and
`actions-v2` — strictly less work than an upstream provider bump, and
trivially replaceable when the upstream catches up.

**Why `replaceOnChanges` on the identity tuple:** Zitadel keys the
link by `(userId, idpId, externalUserId)` and exposes no in-place
modification endpoint. The provider's `update()` is a no-op, so any
change to those three fields MUST be routed through delete + create.
Pulumi only does that when the resource sets `replaceOnChanges` (or
the provider implements `diff()` returning `replaces`). Without it, a
sub-claim typo in ESC would silently update Pulumi state to the new
value while leaving Zitadel pointing at the old sub — silently
re-introducing the dead-end this design exists to prevent.

**Operational trade-off — sub claim lookup is manual:** the Google
`sub` is opaque and not derivable from email. New admins capture it
once via OAuth Playground or `gcloud auth print-access-token` +
`/oauth2/v2/userinfo`, then write it to ESC. The runbook
(`docs/runbooks/add-zitadel-admin-user.md`) walks the operation. For
small admin teams (<10) this is acceptable overhead. At larger scale,
revisit Option B (`isAutoCreation = true` + an Action that grants
`IAM_OWNER` based on an email allow-list).

## Risks / Trade-offs

- **[Risk]** Dev DB wipe loses all current Zitadel state (orgs, users,
  policies, IdPs, machine keys). → **Mitigation**: this is the intended
  state reset. Verify no human end users exist before wipe (`POST
  /management/v1/users/_search` against the existing instance returns no
  human users — only `pulumi-admin` and `login-client` machine users). All
  Pulumi-managed resources are recreated by `pulumi up` after re-bootstrap.

- **[Risk]** The new `pulumi-admin` SA key generated at re-bootstrap may
  not propagate to GSM before Pulumi tries to authenticate, causing a
  transient race. → **Mitigation**: verify the bootstrap-uploader has run
  to completion (pod log shows `bootstrap-uploader: upload complete`)
  before running `pulumi up`. The sidecar idles after upload, so its
  successful exit message persists in the pod log.

- **[Risk]** Frontend OIDC `client_id` rotation is observed as a regression
  by anyone holding a stale local config. → **Mitigation**: dev ESC drives
  the value, so a fresh `pulumi preview` on the frontend stack picks it up.
  Communicate the change in PR description; tests / CI run against fresh
  config.

- **[Risk]** Console login UX still surprises pannpers if Zitadel v4 routes
  to the `liverty-music` org's policy (passkey-only) instead of `admin`'s
  (Google-enabled). → **Mitigation**: D8's belt-and-braces configuration
  (admin org policy + DefaultLoginPolicy + admin-org verified domain) is
  designed to converge regardless of the routing rule. If empirical
  testing still fails, the fallback is to bookmark `/ui/v2/login?org=<admin
  org id>` for the admin entry point.

- **[Risk]** Sub-claim typo in ESC silently breaks first sign-in. Pulumi
  creates the link record successfully (the API does not validate the
  sub against Google), but the IdP callback's actual sub never matches,
  so the admin hits `/ui/v2/login/idp/google/account-not-found`.
  → **Mitigation**: post-deploy smoke test
  (`docs/runbooks/add-zitadel-admin-user.md` Step 6) confirms the sign-in
  lands on Console. The runbook's Step 1 also documents how to capture
  the sub deterministically (OAuth Playground or `gcloud auth
  print-access-token` + `/oauth2/v2/userinfo`) to keep the typo surface
  small. Re-running the smoke test after every admin-onboarding PR is
  the operational guard.

- **[Risk]** Google OAuth client secret leak → attacker can mint Google
  identities from this client and sign in as any pre-provisioned admin
  email. → **Mitigation**: secret stored only in encrypted ESC, never in
  git or k8s manifests. Rotation via `esc env set --secret` + Pulumi up.

- **[Trade-off]** Re-bootstrap regenerates `pulumi-admin`'s SA key. The
  old key in any operator's local cache becomes invalid. Operators should
  re-fetch the latest version from GSM after the migration step.

- **[Trade-off]** Two orgs is more concept to onboard than one, but the
  benefit is reusing Cloud's mental model and cleanly supporting future
  admin / product expansion.

## Migration Plan

**Phase 1 — Specification merge (no infra change):** This OpenSpec change
merges first. No runtime effect on dev.

**Phase 2 — Cloud-provisioning implementation in dev (one PR):**

1. Edit `k8s/namespaces/zitadel/base/configmap.env`: add
   `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`.
2. Edit `src/zitadel/constants.ts`: replace `ZITADEL_DEV_DEFAULT_ORG_ID`
   with admin / product org id refs (initial admin id placeholder, will
   update post-bootstrap).
3. Edit `src/zitadel/index.ts` and components: introduce
   `zitadel.Org liverty-music`, move Project / ApplicationOidc /
   LoginPolicy / login-client to it, add Google IdP / HumanUser /
   InstanceMember in admin org.
4. Verify no human users exist in current dev Zitadel (`POST
   /management/v1/users/_search` with type filter HUMAN, must return zero
   results).
5. Drop dev Zitadel database in Cloud SQL: `DROP DATABASE zitadel; CREATE
   DATABASE zitadel OWNER "zitadel@liverty-music-dev.iam";` via the
   Cloud SQL Auth Proxy + IAM auth.
6. Trigger Zitadel pod restart (delete the `zitadel` Deployment's pods so
   they re-roll). Watch pod logs for `start-from-init` completing setup.
7. Wait for `bootstrap-uploader: upload complete` in the new pod's logs;
   confirm `zitadel-admin-sa-key` GSM secret has a new latest version.
8. Inspect the new admin org id via `POST /admin/v1/orgs/_search` with the
   new SA key; record the id and update `constants.ts` admin org id.
9. Run `pulumi preview` to confirm: new `liverty-music` org created,
   product resources placed there, IdP / HumanUser / InstanceMember
   created in admin org.
10. `pulumi up`. Capture new `liverty-music` org id and product
    `ApplicationOidc` `client_id` from outputs.
11. Trigger frontend stack `pulumi up` (or merge a frontend PR if the
    rotation is gated). Verify SPA can complete OIDC flow.
12. Smoke test: `pannpers@pannpers.dev` opens
    `https://auth.dev.liverty-music.app/ui/console`, signs in via Google,
    confirms Console loads with `IAM_OWNER`.

**Rollback:** `pulumi destroy` of the new product / IdP / HumanUser /
InstanceMember resources (in reverse dependency order). The dev DB is
already empty of end users; restoring "the previous state" requires a
second wipe + re-bootstrap with the *old* configmap. Given the absence of
production data, rollback is "wipe again, restore old configmap, pulumi
up". The `pulumi-admin` SA key in GSM continues to authenticate Pulumi
across these cycles.

**Phase 3 — Staging / prod adoption (separate change):** No DB wipe
needed. configmap with `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin` is in place
from the start; `pulumi up` provisions everything cleanly on the first
deploy.

## Open Questions

*All previously open questions have been resolved during implementation
and smoke testing — see "Resolved" sections below.*

## Resolved (during cutover smoke test, after PR #228 merge)

- **Console login routing in Zitadel v4** — empirically established:
  Login V2 uses the **default org's own `LoginPolicy`** when the
  incoming OIDC AuthN omits `org_id` (which the Zitadel-internal
  Console always does). Captured in D8.

- **`login-client` PAT recreation across re-bootstrap** — confirmed:
  the `MachineUser` recreated in the new `admin` org regenerates a
  fresh PAT value via `PersonalAccessToken`, and the `ExternalSecret`
  reading it from GSM picks up the new value cleanly. The Login V2
  pod was restarted as part of the rollout to flush the in-memory PAT
  cache; first sign-in attempt after restart succeeded.

- **First-sign-in dead-end when admin org's policy disables both
  userLogin and auto-creation** — surfaced after PR #228, resolved by
  pre-linking the Google identity via `ZitadelUserIdpLink`. Captured
  in D11.

## Resolved (during pre-flight Section 1)

- **`@pulumiverse/zitadel` field names** — `IdpGoogle` uses
  `clientId` / `clientSecret` / `scopes` / `name` /
  `isLinkingAllowed` / `isCreationAllowed` / `isAutoCreation` /
  `isAutoUpdate`. There is no policy-level `autoLinking` /
  `userLinking` field in `LoginPolicy` or `DefaultLoginPolicy`; auto-link
  behaviour is governed entirely by IdP-level `isLinkingAllowed`. See D5
  above.
- **`HumanUser.isEmailVerified` constraint** — the field can only be
  `true` at creation time if `initialPassword` is also set. Resolved by
  setting a random throwaway `initialPassword`, paired with
  `LoginPolicy.userLogin = false` on the `admin` org so the password is
  unreachable. See D5.
- **Login V2 IdP callback URL format** — fixed at
  `${CUSTOM_DOMAIN}/idps/callback` in v4 (does not include the IdP id).
  For dev: `https://auth.dev.liverty-music.app/idps/callback`. This is
  the value to register on the Google OAuth client's authorised redirect
  URI list.
- **Default org marker** — `zitadel.Org` resource accepts `isDefault`
  directly. No separate API call required.
- **Existing user inventory** — verified that the dev Zitadel instance
  has 2 human users (`zitadel-admin@...` bootstrap default; user pannpers'
  `pepperoni9@gmail.com` test account). The latter has been deleted via
  `DELETE /management/v1/users/{id}` ahead of the planned database wipe;
  the former will be re-generated cleanly by re-bootstrap. There is also
  a `backend-app` machine user (Pulumi-managed product service identity)
  that belongs in the `liverty-music` product org per the updated
  "Place Machine Users by Responsibility" requirement.
