## Context

The hosted login is Zitadel's Login V2 (a Next.js app, upstream image `ghcr.io/zitadel/zitadel-login`), deployed by the official Zitadel Helm chart 10.4.0 from `cloud-provisioning/k8s/namespaces/zitadel/`. One Login V2 deployment serves every organization: the product org (fans), every Organizer's Organization and the admin org. Production runs Zitadel v4.20.0 (cloud-provisioning#710).

Why a setting cannot fix it: see proposal.md. At v4.20.0 the Login V2 source has these password-setup paths, all of which the spec closes:

| Entry | Source at v4.20.0 |
|---|---|
| Passkey/Password radio on sign-up; Password continues to `/register/password` | `apps/login/src/components/register-form.tsx:160-199`, `lib/server/register.ts:82` (`addHumanUser` with `password`) |
| Password option when choosing a credential to set up (invitation, first sign-in) | `components/choose-authenticator-to-setup.tsx:24` |
| `/password/set` (reset code or direct address) | `app/(login)/password/set/page.tsx`, `components/set-password-form.tsx:70,104` |
| `/password/change` (signed-in self-service) | `app/(login)/password/change/page.tsx`, `lib/self.ts:37` |
| Password reset request on the password page | `components/password-form.tsx:75` (link hidden by `hidePasswordReset`, code path still present) |

`/password` (sign-in with an existing password) stays: the automated end-to-end test fans in production sign in with it (`cloud-provisioning` `E2eTestUserComponent`, commits 4ce2a78 and 4d3b524).

## Goals / Non-Goals

**Goals:**
- The production hosted login sets no password from any page, for every organization it serves.
- Upgrading Zitadel stays one tag bump plus a rebuild; a patch that no longer fits the new source fails loudly before anything is deployed.

**Non-Goals:**
- Blocking password setup through the Zitadel Console's self-service pages or direct API calls (accepted residual risk; see Risks).
- A login-policy setting for "passkeys only" (that is upstream zitadel/zitadel#11682).
- Any other Login V2 customization (copy, layout, fields).

## Decisions

### D1. Patch the Login V2 source; keep the API image upstream

The patch changes only `apps/login`. The Zitadel API image stays `ghcr.io/zitadel/zitadel:<tag>`.

- Alternative: fork Zitadel core and add a passkeys-only policy value. Rejected: it changes the API, the proto and the Console, and the fork would have to follow every upstream release of the whole server (five releases between 2026-09-28 and 2026-10-22, several of them security fixes).
- Alternative: reject password-setting API calls with a Zitadel Actions v2 request execution and leave the UI as is. Rejected as the primary fix: a person who picks Password still sees the choice and then an error. It remains the follow-up for the residual risk.

### D2. What the patch does

- Sign-up: render the passkey path only (no `AuthenticationMethodRadio`, always continue without a password).
- Credential choice: drop the Password option from `ChooseAuthenticatorToSetup`.
- `/register/password`, `/password/set`, `/password/change`: the page calls Next.js `notFound()` before rendering, so a typed address shows the hosted login's not-found page.
- Password page: remove the reset-request handler from `PasswordForm`, not only the hidden link.
- Server actions: a page that calls `notFound()` stops rendering, but the Next.js Server Actions it used (`"use server"` in `lib/server/register.ts`, `lib/server/password.ts`, `lib/self.ts`) stay callable endpoints. The patch makes them refuse a password: `registerUser` returns an error when `password` is set, and `resetPassword`, `changePassword` and `setMyPassword` return an error without calling the Zitadel API. Login V2 is Zitadel's own Next.js app; Liverty Music's apps do not use Next.js.
- `/password` sign-in is untouched.

The patch is unconditional (no feature flag): every organization the deployment serves is passkey-only or IdP-only (the admin org signs in with Google), so there is no organization that needs the password paths. A flag would add a setting nobody turns on.

### D3. Build from the upstream tag plus a patch file, in `cloud-provisioning`

`cloud-provisioning` gets a `zitadel-login/` directory holding:
- `UPSTREAM_TAG` with the Zitadel tag (it must equal `image.tag` in `k8s/namespaces/zitadel/base/values.yaml`);
- `patches/*.patch` in `git format-patch` form against `zitadel/zitadel` at that tag;
- a GitHub Actions workflow that checks out `zitadel/zitadel` at the tag, runs `git am` with the patches, runs the upstream build (`pnpm install --frozen-lockfile`, `pnpm nx run @zitadel/login:pack`, which depends on `build`), and pushes the image to Artifact Registry as `<region>-docker.pkg.dev/liverty-music-prod/zitadel-login/zitadel-login:<tag>-lm.<n>`, where `<n>` is the patch revision.

- Alternative: a GitHub fork of `zitadel/zitadel` under `liverty-music`. Rejected: a new repository needs its own WIF binding, environments and branch rules in the GitHub Pulumi program, and each upgrade is a rebase of a large monorepo branch. A patch file states the whole delta in one reviewable file and its failure to apply is the upgrade signal.
- Alternative: a new repository holding only the patch and workflow. Rejected for the same provisioning cost; `cloud-provisioning` already owns the Zitadel deployment and its GitHub Actions can already impersonate the `github-actions` service account, which holds `roles/artifactregistry.writer` on the project (`src/gcp/components/workload-identity.ts`).

The workflow runs on changes under `zitadel-login/` on `main` and by `workflow_dispatch`. It does not deploy: the image tag in `values.yaml` is bumped by a normal PR after the image exists, so ArgoCD never points at a missing image.

### D4. Artifact Registry repository and pull access via Pulumi

A new Docker repository `zitadel-login` in the production project, next to `backend` and `frontend` in `src/gcp/index.ts`, and a reader binding for the GKE node service account the same way `kubernetes.ts` binds the existing registries. Dev gets no repository: its workload is disabled and the dev overlay keeps the upstream image.

### D5. Helm wiring

Only production runs the patched image. `k8s/namespaces/zitadel/overlays/prod/values.yaml` sets `login.image.repository` to the Artifact Registry path and `login.image.tag` to `<tag>-lm.<n>`; `base/values.yaml` keeps the upstream image, which the disabled dev overlay inherits. The chart (10.4.0) takes both keys as plain values, so Helm rendering through Kustomize and ArgoCD is unchanged.

### D6. Upgrade procedure

A Zitadel upgrade PR changes `UPSTREAM_TAG`; a lint check keeps `UPSTREAM_TAG` equal to the base `image.tag` and the prod overlay's `login.image.tag` starting with `UPSTREAM_TAG`; the workflow rebuilds and must succeed before the PR that bumps `image.tag` and `login.image.tag` together merges. If `git am` fails, the patch is refreshed against the new tag in the same PR. The runbook `docs/runbooks/zitadel-helm-chart.md` gains this step.

### D7. Verification lives in the frontend production E2E

The patch itself sits in `cloud-provisioning`, but the scenario coverage check reads `@spec` annotations from test files on the implementing repositories' `main`, and the behavior is only observable in the deployed hosted login. The `frontend` production Playwright suite (`playwright.prod.config.mjs`, `e2e/prod/`) already drives that hosted login, so:

- a new guest spec covers "Sign-up offers only a passkey", "Password pages opened by address", "No password reset on the password page" and the organizer "Set-password page opened by address";
- "Choosing a credential to set up offers no password" and the organizer "Invited person chooses a credential" need an identity that has no credential yet, which the guest flow does not reach without an invitation; they are covered with `@spec-manual` and a recorded production check after the rollout;
- "Existing password still signs in" is annotated on the step that signs the production test fan in with its password (`scripts/capture-auth-state-password.ts` or the spec that exercises it).

`e2e/prod/delete-my-account.guest.spec.ts` signs a fresh fan up with a password today (lines 29-30, 111-112). It moves to a passkey from Playwright's virtual authenticator (`context.credentials`), the mechanism the organizer test member already uses (`docs/prod-e2e-fixtures.md`). Its fresh sign-in before deletion then uses that passkey.

## Risks / Trade-offs

- [A person sets a password through the Zitadel Console self-service or the API directly] → Accepted for launch: it affects only that person's own identity. Before implementation, confirm whether a fan identity can reach the Console at all; if it can and the Console lets a password be set, add the Actions v2 request execution rejecting password-setting methods (exempting the Pulumi admin machine user that creates the end-to-end test fans) as a follow-up change.
- [The patch drifts from upstream and an upgrade is blocked] → The build fails before deploy; the patch touches five files, so a refresh is small. Upstream zitadel/zitadel#11682 may make the patch unnecessary; drop it then.
- [The production E2E that deletes an account breaks on the day the patched image rolls out] → The frontend change to passkey sign-up merges and passes against the upstream image first (the passkey path exists there too), before the image switch.
- [A security release needs a fast upgrade] → The rebuild runs in CI from the tag; no local toolchain is needed.
- [The patched image differs from upstream beyond the patch] → The build uses the upstream lockfile and nx target unchanged.

## Migration Plan

1. Pulumi: Artifact Registry repository and node reader binding; prod `pulumi up` (by the user).
2. Merge the `zitadel-login/` directory; the workflow pushes `v4.20.0-lm.1`.
3. Merge the values change pointing prod at the image. ArgoCD rolls the Login V2 pod.
4. Verify in production (tasks). Rollback: revert step 3, which returns to the upstream image of the same tag.
