## Context

The hosted login is Zitadel's Login V2 (a Next.js app, upstream image `ghcr.io/zitadel/zitadel-login`), deployed by the official Zitadel Helm chart 10.4.0 from `cloud-provisioning/k8s/namespaces/zitadel/`. One Login V2 deployment serves every organization: the product org (fans), every Organizer's Organization and the admin org. Production runs Zitadel v4.20.0 (cloud-provisioning#710). Login V2 is Zitadel's own Next.js app; Liverty Music's apps do not use Next.js.

Why a setting cannot fix it: see proposal.md. At v4.20.0 the Login V2 source has these password-setup paths, all of which the spec closes:

| Entry | Page or component at v4.20.0 | Server action (`"use server"`) that sets the password |
|---|---|---|
| Passkey/Password radio on sign-up; Password continues to `/register/password` | `apps/login/src/components/register-form.tsx:160-199` | `registerUser` (`lib/server/register.ts:61`, `addHumanUser` with `password` at :82) |
| Password option when choosing a credential to set up (invitation, first sign-in) | `components/choose-authenticator-to-setup.tsx:24` | leads to `/password/set` |
| `/password/set` (reset code or direct address) | `app/(login)/password/set/page.tsx`, `components/set-password-form.tsx:70,104` | `resetPassword` (`lib/server/password.ts:46`), `changePassword` (:449) |
| `/password/change` (signed-in self-service, and the redirect for a forced or expired password) | `app/(login)/password/change/page.tsx`, `components/change-password-form.tsx:59` | `checkSessionAndSetPassword` (`lib/server/password.ts:498`) |
| Password reset request on the password page | `components/password-form.tsx:75` (link hidden by `hidePasswordReset`, code path still present) | `resetPassword` |
| none (exported, no caller at v4.20.0) | none | `setMyPassword` (`lib/self.ts:14`) |

The other server actions that create users do not take a password: `registerUserAndLinkToIDP` (`lib/server/register.ts:200`) and the IdP intent's `createUser` (`lib/server/idp-intent.ts`) build the user from the IdP's data. `sendPassword` (`lib/server/password.ts:139`) checks an existing password for sign-in and stays.

`/password` (sign-in with an existing password) stays: the automated end-to-end test fans in production sign in with it (`cloud-provisioning` `E2eTestUserComponent`, commits 4ce2a78 and 4d3b524).

## Goals / Non-Goals

**Goals:**
- The production hosted login sets no password, from any page or by calling its server directly, for every organization it serves.
- Upgrading Zitadel stays one tag bump plus a rebuild; a patch that no longer fits the new source fails before anything is deployed.

**Non-Goals:**
- Blocking password setup through the Zitadel Console's self-service pages or direct Zitadel API calls (accepted residual risk; see Risks).
- A login-policy setting for "passkeys only" (that is upstream zitadel/zitadel#11682).
- Any other Login V2 customization (copy, layout, fields).

## Decisions

### D1. Patch the Login V2 source; keep the API image upstream

The patch changes only `apps/login`. The Zitadel API image stays `ghcr.io/zitadel/zitadel:<tag>`.

- Alternative: fork Zitadel core and add a passkeys-only policy value. Rejected: it changes the API, the proto and the Console, and the fork would have to follow every upstream release of the whole server (five releases between 2026-09-28 and 2026-10-22, several of them security fixes).
- Alternative: reject password-setting API calls with a Zitadel Actions v2 request execution and leave the UI as is. Rejected as the primary fix: a person who picks Password still sees the choice and then an error. It remains the follow-up for the residual risk.

### D2. What the patch does

- Sign-up: render the passkey path only (no `AuthenticationMethodRadio`, always continue without a password).
- Credential choice: drop the Password option from `ChooseAuthenticatorToSetup`. External IdP buttons on the same page stay, because Organizers' Organizations allow federation.
- `/register/password`, `/password/set`, `/password/change`: the page calls Next.js `notFound()` before rendering, so a typed address shows the hosted login's not-found page.
- Password page: remove the reset-request handler from `PasswordForm`, not only the hidden link.
- Server actions: a page that calls `notFound()` stops rendering, but a Next.js Server Action stays a callable endpoint. The patch makes every action in the table above refuse: `registerUser` returns an error when `password` is set, and `resetPassword`, `changePassword`, `checkSessionAndSetPassword` and `setMyPassword` return an error without calling the Zitadel API. Each refusal has a unit test in the patch.
- `/password` sign-in (`sendPassword`) is untouched.

The patch is unconditional (no feature flag): every organization the deployment serves is passkey-only or IdP-only (the admin org signs in with Google), so there is no organization that needs the password paths. A flag would add a setting nobody turns on.

### D3. Build from the upstream tag plus a patch file, in `cloud-provisioning`

`cloud-provisioning` gets a `zitadel-login/` directory holding:
- `UPSTREAM_TAG` with the Zitadel tag;
- `patches/*.patch` in `git format-patch` form against `zitadel/zitadel` at that tag;

and a GitHub Actions workflow that checks out `zitadel/zitadel` at the tag, runs `git am` with the patches, runs the patched app's unit tests, builds with `pnpm install --frozen-lockfile` and `pnpm nx run @zitadel/login:build`, then runs the same `docker build -f apps/login/Dockerfile apps/login` as the upstream `pack` target but tags the result for Artifact Registry (`pack` itself hard-codes `zitadel/zitadel-login:local`, `apps/login/project.json:35`), for `linux/amd64`.

**Image tag.** `<region>-docker.pkg.dev/liverty-music-prod/zitadel-login/zitadel-login:<UPSTREAM_TAG>-lm.<tree>`, where `<tree>` is the first 12 characters of `git rev-parse HEAD:zitadel-login` in `cloud-provisioning`. The tag is a function of the build input: the same `zitadel-login/` content always yields the same tag, and any change to the tag pin or a patch yields a new one. The production repository has immutable tags (`src/gcp/index.ts`, `immutableTags: true` for non-dev), so the workflow skips the push when the tag already exists instead of failing, and never needs a revision counter.

**When it runs.** On pull requests and on `main` when `zitadel-login/` changes, and by `workflow_dispatch`. Building on the pull request means the image exists before the pull request that points production at it merges; the job is a required check for pull requests that touch `zitadel-login/`.

- Alternative: a GitHub fork of `zitadel/zitadel` under `liverty-music`. Rejected: a new repository needs its own WIF binding, environments and branch rules in the GitHub Pulumi program, and each upgrade is a rebase of a large monorepo branch. A patch file states the whole delta in one reviewable file and its failure to apply is the upgrade signal.
- Alternative: a new repository holding only the patch and workflow. Rejected for the same provisioning cost; `cloud-provisioning` already owns the Zitadel deployment and its GitHub Actions can already impersonate the `github-actions` service account, which holds `roles/artifactregistry.writer` on the project (`src/gcp/components/workload-identity.ts`).
- Alternative: build only after merge to `main`, then point production at the image in a second pull request. Rejected: an upgrade needs two pull requests in a fixed order, and the consistency check below cannot hold between them.

### D4. Artifact Registry repository and pull access via Pulumi

A new Docker repository `zitadel-login` in the production project, next to `backend` and `frontend` in `src/gcp/index.ts`, and a reader binding for the GKE node service account the same way `kubernetes.ts` binds the existing registries. Dev gets no repository: its workload is disabled and the dev overlay keeps the upstream image.

### D5. Helm wiring

Only production runs the patched image. `k8s/namespaces/zitadel/overlays/prod/values.yaml` sets `login.image.repository` to the Artifact Registry path and `login.image.tag` to `<UPSTREAM_TAG>-lm.<tree>`; `base/values.yaml` keeps the upstream image, which the disabled dev overlay inherits. The chart (10.4.0) takes both keys as plain values, so Helm rendering through Kustomize and ArgoCD is unchanged.

### D6. Consistency check and upgrade procedure

A check run by `make lint-k8s` fails unless `zitadel-login/UPSTREAM_TAG` equals `image.tag` in `base/values.yaml` and the prod overlay's `login.image.tag` equals `<UPSTREAM_TAG>-lm.<tree>` computed from the checked-out `zitadel-login/`. A Zitadel upgrade is then one pull request: bump `UPSTREAM_TAG`, `image.tag` and the prod `login.image.tag` together, refresh the patch if `git am` fails, wait for the pull request's image build, merge. A patch change without a tag change fails the check, so production can never run an image older than its patch. The runbook `docs/runbooks/zitadel-helm-chart.md` gains this procedure.

### D7. Verification lives in the frontend production E2E

The patch sits in `cloud-provisioning`, but the scenario coverage check reads `@spec` annotations from test files on the implementing repositories' `main` (`scripts/check-scenario-coverage.py`), and `@spec-manual` lines from any of this change's files. The behavior is observable in the deployed hosted login, which the `frontend` production Playwright suite (`playwright.prod.config.mjs`, `e2e/prod/`) already drives, so:

- a new guest spec covers "Sign-up offers only a passkey", "Password pages opened by address", "No password reset on the password page" and the organizer "Set-password page opened by address";
- "Existing password still signs in" is annotated on the step that signs the production test fan in with its password;
- the scenarios no browser test reaches are exempted here, each with the task that records its evidence:

@spec-manual components/infrastructure/fan/web/global/hosted-login "Choosing a credential to set up offers no password" -- re-invite the e2e-test Organizer's test member in production and confirm the credential choice shows Passkey and no Password; task 5.2
@spec-manual components/infrastructure/organizer/web/global/hosted-login "Invited person chooses a credential" -- same production re-invitation, ending at the organizer console after the passkey; task 5.2
@spec-manual components/infrastructure/fan/web/global/hosted-login "Password sent to the hosted login without its pages" -- a Server Action's id changes with every build, so no stable browser test can call it; the patch's unit tests show each password-setting server action refusing without calling the API; task 3.1
@spec-manual components/infrastructure/fan/web/global/hosted-login "Apply Strict Passkeys Policy on product org" -- prod pulumi preview shows the product org login policy unchanged (userLogin true, passwordless allowed, hidePasswordReset true, external IdP off); task 6.1
@spec-manual components/infrastructure/fan/web/global/hosted-login "Admin org isolation" -- prod pulumi preview shows no change to the admin org policy; task 6.1

`e2e/prod/delete-my-account.guest.spec.ts` signs a fresh fan up with a password today (lines 29-30, 111-112). It moves to a passkey from Playwright's virtual authenticator (`context.credentials`), the mechanism the organizer test member already uses (`docs/prod-e2e-fixtures.md`). Its fresh sign-in before deletion then uses that passkey.

## Risks / Trade-offs

- [A person sets a password through the Zitadel Console self-service or the API directly] → Accepted for launch: it affects only that person's own identity. Task 7.1 checks whether a fan identity can set a password in the Console; if it can, add the Actions v2 request execution rejecting password-setting methods (exempting the Pulumi admin machine user that creates the end-to-end test fans) as a follow-up change.
- [An end-to-end test fan is sent to `/password/change` and locked out] → Login V2 redirects there when the identity has `passwordChangeRequired` or its password is older than the password age policy (`lib/verify-helper.ts:24-38`, `lib/server/password.ts:358-368`), and the patch makes that page not found. The test fans sign in with their password today, so neither applies; the invariant is that test fans are created without `passwordChangeRequired` and the product org sets no password age. Rotating a test fan's password goes through Pulumi, not the hosted login.
- [The patch drifts from upstream and an upgrade is blocked] → The build fails on the pull request, before anything deploys; the patch touches a handful of files, so a refresh is small. Upstream zitadel/zitadel#11682 may make the patch unnecessary; drop it then.
- [The production E2E that deletes an account breaks on the day the patched image rolls out] → The frontend change to passkey sign-up merges and passes against the upstream image first (the passkey path exists there too), before the image switch.
- [A security release needs a fast upgrade] → The rebuild runs in CI from the tag; no local toolchain is needed.
- [The patched image differs from upstream beyond the patch] → The build uses the upstream lockfile, the upstream `build` target and the upstream Dockerfile unchanged.
- [Rollback re-opens password setup] → Reverting to the upstream image of the same tag restores every password page; do it only to recover from a broken login, and re-apply the patched image as soon as it is fixed. The API image is unaffected by a Login V2 rollback.

## Migration Plan

1. Pulumi: Artifact Registry repository and node reader binding; prod `pulumi up` (by the user).
2. One pull request adds `zitadel-login/`, the workflow, the consistency check and the prod `login.image` values; its pull-request build pushes `v4.20.0-lm.<tree>`, then it merges and ArgoCD rolls the Login V2 pod.
3. Verify in production (tasks). Rollback: revert the prod `login.image` values, which returns to the upstream image of the same tag (see Risks).
