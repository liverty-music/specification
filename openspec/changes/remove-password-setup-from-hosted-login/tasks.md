## 1. frontend: production E2E no longer signs up with a password

- [ ] 1.1 Move `e2e/prod/delete-my-account.guest.spec.ts` from password sign-up to a passkey from Playwright's virtual authenticator (`context.credentials`), including the fresh sign-in before deletion, and verify `npm run test:e2e:prod -- delete-my-account` passes against production while it still runs the upstream Login V2 image
- [ ] 1.2 Annotate the production test fan's password sign-in with `@spec components/infrastructure/fan/web/global/hosted-login "Existing password still signs in"` and verify `npm run auth:capture:password:prod` still signs in

## 2. cloud-provisioning: Artifact Registry for the patched Login V2 (design D4)

- [ ] 2.1 Add the `zitadel-login` Docker repository in `src/gcp/index.ts` next to `backend` and `frontend`, and the GKE node service account reader binding in `src/gcp/components/kubernetes.ts`; verify the Pulumi Cloud preview on the PR shows only those additions
- [ ] 2.2 After merge, have the user run the prod `pulumi up`, and verify `gcloud --configuration=liverty-music artifacts repositories describe zitadel-login --location=asia-northeast2` succeeds

## 3. cloud-provisioning: patch and build (design D2, D3)

- [ ] 3.1 Add `zitadel-login/UPSTREAM_TAG` (`v4.20.0`) and `zitadel-login/patches/0001-*.patch` made with `git format-patch` against `zitadel/zitadel` at that tag, implementing D2 (sign-up passkey only, no Password in the credential choice, `notFound()` on `/register/password`, `/password/set`, `/password/change`, no reset request in the password form, `/password` untouched, and `registerUser`, `resetPassword`, `changePassword` and `setMyPassword` refuse a password without calling the API); verify `git am` applies cleanly on a fresh checkout of the tag, a unit test per server action shows the refusal, and the patched `apps/login` unit tests pass (`pnpm nx run @zitadel/login:test`)
- [ ] 3.2 Add the GitHub Actions workflow that checks out the tag, applies the patches, runs `pnpm nx run @zitadel/login:pack` and pushes `zitadel-login:<tag>-lm.<n>` through the existing `github-actions` service account; after merge, verify the push-triggered run pushes `v4.20.0-lm.1` (`gcloud artifacts docker tags list`)
- [ ] 3.3 Add a check that `zitadel-login/UPSTREAM_TAG` equals `image.tag` in `k8s/namespaces/zitadel/base/values.yaml` and that `login.image.tag` in `k8s/namespaces/zitadel/overlays/prod/values.yaml` starts with `UPSTREAM_TAG`, run in `make lint-k8s`, and verify it fails when either differs
- [ ] 3.4 Add the upgrade step (bump `UPSTREAM_TAG`, rebuild, refresh the patch if `git am` fails, then bump both image tags) to `docs/runbooks/zitadel-helm-chart.md`

## 4. cloud-provisioning: run the patched image in production (design D5)

- [ ] 4.1 Set `login.image.repository` and `login.image.tag` in `k8s/namespaces/zitadel/overlays/prod/values.yaml`; verify the prod render shows the Artifact Registry image only on the Login V2 Deployment, the dev render keeps the upstream image, and `make lint-k8s` passes
- [ ] 4.2 After merge, verify ArgoCD is `Synced Healthy`, the `zitadel-api-login` pod runs the patched image with 0 restarts, and its log has no errors for 15 minutes

## 5. frontend: production checks of the closed pages

- [ ] 5.1 Add `e2e/prod/hosted-login-offers-no-password-setup.guest.spec.ts` covering fan hosted-login "Sign-up offers only a passkey", "Password pages opened by address" and "No password reset on the password page", and organizer hosted-login "Set-password page opened by address", each with its `@spec` annotation; verify it passes against production after 4.2
- [ ] 5.2 Record `@spec-manual` for fan hosted-login "Choosing a credential to set up offers no password" and organizer hosted-login "Invited person chooses a credential", verified by re-inviting the `e2e-test` Organizer's test member in production and confirming the credential choice shows Passkey only; record the date in this task
- [ ] 5.3 Verify `npm run test:e2e:prod` passes in full against production with the patched image

## 6. Unchanged login policy scenarios

- [ ] 6.1 Run the prod `pulumi preview` and confirm the product org and admin org login policies are unchanged, then record `@spec-manual components/infrastructure/fan/web/global/hosted-login "Apply Strict Passkeys Policy on product org" -- prod pulumi preview shows the product org login policy unchanged (userLogin true, passwordless allowed, hidePasswordReset true, external IdP off)` and `@spec-manual components/infrastructure/fan/web/global/hosted-login "Admin org isolation" -- prod pulumi preview shows no change to the admin org policy` in this task

## 7. Residual risk check

- [ ] 7.1 Sign in to `https://auth.liverty-music.app/ui/console` as a production test fan and record whether the Console lets the fan set a password; if it does, open a follow-up issue for the Actions v2 request execution described in design Risks
