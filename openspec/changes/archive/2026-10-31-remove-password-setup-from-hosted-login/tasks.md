## 1. frontend: production E2E no longer signs up with a password

- [x] 1.1 Move `e2e/prod/delete-my-account.guest.spec.ts` from password sign-up to a passkey from Playwright's virtual authenticator (`context.credentials`), including the fresh sign-in before deletion, and verify `npm run test:e2e:prod -- delete-my-account` passes against production while it still runs the upstream Login V2 image
- [x] 1.2 Annotate the production test fan's password sign-in with `@spec components/infrastructure/fan/web/global/hosted-login "Existing password still signs in"` and verify `npm run auth:capture:password:prod` still signs in

## 2. cloud-provisioning: Artifact Registry for the patched Login V2 (design D4)

- [x] 2.1 Add the `zitadel-login` Docker repository in `src/gcp/index.ts` next to `backend` and `frontend`, and the GKE node service account reader binding in `src/gcp/components/kubernetes.ts`; verify the Pulumi Cloud preview on the PR shows only those additions
- [x] 2.2 After merge, have the user run the prod `pulumi up`, and verify `gcloud --configuration=liverty-music artifacts repositories describe zitadel-login --location=asia-northeast2` succeeds

## 3. cloud-provisioning: patch, build and production wiring in one pull request (design D2, D3, D5, D6)

- [x] 3.1 Add `zitadel-login/UPSTREAM_TAG` (`v4.20.0`), `zitadel-login/build.sh` (D3: checkout, `git am`, unit tests, build, `docker build`) and `zitadel-login/patches/0001-*.patch` made with `git format-patch` against `zitadel/zitadel` at that tag, implementing D2: sign-up passkey only; no Password in the credential choice (IdP buttons kept); `notFound()` on `/register/password`, `/password/set` and `/password/change`; no reset request in the password form; `registerUser` refuses a `password`, and `resetPassword`, `changePassword`, `checkSessionAndSetPassword` and `setMyPassword` return an error without calling the API; `/password` sign-in untouched. Verify `git am` applies cleanly on a fresh checkout of the tag, one unit test per server action shows its refusal (the evidence for the design's `@spec-manual` "Password sent to the hosted login without its pages"), and `pnpm nx run @zitadel/login:test` passes
- [x] 3.2 Add the GitHub Actions workflow of D3, which runs `zitadel-login/build.sh` and holds no build step of its own; the image is tagged `zitadel-login:<UPSTREAM_TAG>-lm.<tree>` (`<tree>` = first 12 characters of `git rev-parse HEAD:zitadel-login`). On pull requests touching `zitadel-login/` it stops after the build, with no Google Cloud authentication, and is a required check; on `main` and `workflow_dispatch` on `main` it pushes through the existing `github-actions` service account unless the tag already exists. Verify the pull request's run builds without pushing, and after merge the `main` run pushes the tag (`gcloud artifacts docker tags list`) and a re-run skips the push
- [x] 3.3 Add the D6 check to `make lint-k8s`: `zitadel-login/UPSTREAM_TAG` equals `image.tag` in `k8s/namespaces/zitadel/base/values.yaml`, and `login.image.tag` in `k8s/namespaces/zitadel/overlays/prod/values.yaml` equals `<UPSTREAM_TAG>-lm.<tree>`; verify it fails when the tag pin, the base image tag or a patch changes without the matching prod tag, fails when the prod overlay has no `login.image` override, passes with no override only while `zitadel-login/ROLLBACK` exists, and fails when `ROLLBACK` and an override exist together
- [x] 3.4 Set `login.image.repository` and `login.image.tag` in `k8s/namespaces/zitadel/overlays/prod/values.yaml`; verify the prod render shows the Artifact Registry image only on the Login V2 Deployment, the dev render keeps the upstream image, and `make lint-k8s` passes
- [x] 3.5 Add the D6 upgrade procedure and the rollback procedure (delete the prod `login.image` override and add `zitadel-login/ROLLBACK` with the reason; it re-opens password setup; restoring re-adds the override and deletes `ROLLBACK` in the same pull request) to `docs/runbooks/zitadel-helm-chart.md`
- [x] 3.6 After the pull request's build passes, merge; verify the `main` run pushed the tag, ArgoCD is `Synced Healthy`, the `zitadel-api-login` pod runs the patched image with 0 restarts, and its log has no errors for 15 minutes

## 4. frontend: production checks of the closed pages

- [x] 4.1 Add `e2e/prod/hosted-login-offers-no-password-setup.guest.spec.ts` covering fan hosted-login "Password pages opened by address" and "No password reset on the password page", and organizer hosted-login "Set-password page opened by address", each with its `@spec` annotation; verify it passes against production after 3.6; "Sign-up offers only a passkey" is annotated on `delete-my-account`'s sign-up (asserts no Password choice, then continues to passkey registration)
  - 2026-10-30: against the patched image, `hosted-login-offers-no-password-setup` and `delete-my-account`: `5 passed (58.5s)`.
- [x] 4.2 Verify `npm run test:e2e:prod` passes in full against production with the patched image
  - 2026-10-30: full `npm run test:e2e:prod` with `zitadel-login:v4.20.0-lm.92ec5f51b8f9`: 20 passed, 2 failed, 1 did not run; both failures came from new purchase fixtures that reused existing fixture events (an event is per venue/date/start-time slot), not from the hosted login. After new unlisted and sale fixtures on free dates, `open-a-shared-event-link.guest` and `buy-tickets-first-come`: 9 passed (34.6m).

## 5. Production checks recorded as @spec-manual (design D7)

- [x] 5.1 After 3.6, confirm the production test fans still sign in with their passwords without being sent to `/password/change` (design Risks: no `passwordChangeRequired`, no password age on the product org)
  - 2026-10-30: with `zitadel-login:v4.20.0-lm.92ec5f51b8f9` live, `open-a-shared-event-link` "returns a guest who follows and signs up…" (test fan password sign-in) passed and returned to the event page, not `/password/change`.
- [x] 5.2 Re-invite the `e2e-test` Organizer's test member in production, confirm the credential choice shows Passkey and no Password and that enrolling the passkey ends at the organizer console, and record the date here; this is the evidence for the design's `@spec-manual` lines "Choosing a credential to set up offers no password" and "Invited person chooses a credential"
  - 2026-10-30: re-invited the e2e-test Organizer's test member (provisioner key: removed the passkey, `CreateInviteCode` with `returnCode`, opened the `/verify?…&invite=true` link with Playwright's virtual authenticator). `/ui/v2/login/authenticator/set` offered only パスキー (Password option count 0); after enrolling the passkey the person arrived at `organizer.liverty-music.app/organizers/01a124ae-…`. The new passkey then signed in alone (`.auth/passkey-signin.mjs`). Key file deleted.

## 6. Unchanged login policy scenarios

- [x] 6.1 Run the prod `pulumi preview` and confirm the product org and admin org login policies are unchanged; this is the evidence for the design's `@spec-manual` lines "Apply Strict Passkeys Policy on product org" and "Admin org isolation"
  - 2026-10-30: prod `pulumi preview` (origin/main after cloud-provisioning#712) shows no LoginPolicy change; state: product org `default` userLogin true, passwordlessType ALLOWED, hidePasswordReset true, allowExternalIdp false; `admin-org-login-policy` separate, allowExternalIdp true.

## 7. Residual risk check

- [x] 7.1 Sign in to `https://auth.liverty-music.app/ui/console` as a production test fan and record whether the Console lets the fan set a password; if it does, open a follow-up issue for the Actions v2 request execution described in design Risks
  - 2026-10-30: yes. The e2e test fan signs in to the Console (login-name page with the product org's `organization`), and "Password and Security" links to `/ui/console/users/me/password`. Follow-up: [cloud-provisioning#714](https://github.com/liverty-music/cloud-provisioning/issues/714).

## 8. Refuse password-setting Zitadel API calls (design D8)

- [x] 8.1 backend: a webhook handler for Zitadel Actions v2 requests that verifies the signature, logs the caller's user id and the method, and always answers with a non-2xx status; unit tests show it refusing a signed request and rejecting an unsigned one
  - backend#738, released in v1.112.0 (2026-10-31); `go test ./internal/adapter/webhook/` covers 403 for each method, 401 unsigned, 503 without the key, 405 non-POST.
- [x] 8.2 cloud-provisioning: a `ZitadelTarget` (`REST_CALL`, `interruptOnError: true`) pointing at that handler, `ZitadelExecutionRequest`s for `/zitadel.user.v2.UserService/SetPassword`, `/zitadel.user.v2.UserService/PasswordReset` and `/zitadel.auth.v1.AuthService/UpdateMyPassword`, and the route and signing key the handler needs (GSM/ESO); verify the Pulumi Cloud preview shows only those additions
  - cloud-provisioning#717 (Target and request executions, Secret Manager key) and #718 (fan-api ExternalSecret, after the secret existed); Pulumi Cloud preview showed only those creates besides existing drift.
- [x] 8.3 After the backend release and the prod `pulumi up`, confirm the three executions are registered on the instance
  - 2026-10-31: prod update v290 `create: 9`; state holds Target `password-setup-refusal-webhook` (`interruptOnError: true`, endpoint `…:9090/refuse-password-setup`) and request executions on `/zitadel.user.v2.UserService/SetPassword`, `/zitadel.user.v2.UserService/PasswordReset`, `/zitadel.auth.v1.AuthService/UpdateMyPassword` (Zitadel accepted the v1 method). fan-api runs `api:v1.112.0`.
- [x] 8.4 In production, signed in to the Console as a test fan: SetPassword from the Console's password page (gRPC-web) and through REST (`curl` with the Console's token) are refused and logged by the handler; the fan still signs in with the old password; the prod `pulumi preview` shows no change to the test fans' passwords
  - 2026-10-31 as `e2e-test-password@liverty-music.app` signed in to the Console, with the current password as the "new" one: the Console's password page (gRPC-web `UserService/SetPassword`) answered `grpc-status 9` `Execution failed (EXEC-dra6yamk98)`; REST `POST /v2/users/{id}/password`, `PUT /auth/v1/users/me/password` and `POST /v2/users/{id}/password_reset` with the Console's token answered `400` with the same error; fan-api logged `refuse-password-setup: refused a password-setting request` with each method and the user id. `npm run auth:capture:password:prod` then signed in with the old password (`Smoke test PASSED`); prod `pulumi preview`: only the existing PostHog insight drift.
