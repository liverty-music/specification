## 1. frontend: production E2E no longer signs up with a password

- [ ] 1.1 Move `e2e/prod/delete-my-account.guest.spec.ts` from password sign-up to a passkey from Playwright's virtual authenticator (`context.credentials`), including the fresh sign-in before deletion, and verify `npm run test:e2e:prod -- delete-my-account` passes against production while it still runs the upstream Login V2 image
- [ ] 1.2 Annotate the production test fan's password sign-in with `@spec components/infrastructure/fan/web/global/hosted-login "Existing password still signs in"` and verify `npm run auth:capture:password:prod` still signs in

## 2. cloud-provisioning: Artifact Registry for the patched Login V2 (design D4)

- [ ] 2.1 Add the `zitadel-login` Docker repository in `src/gcp/index.ts` next to `backend` and `frontend`, and the GKE node service account reader binding in `src/gcp/components/kubernetes.ts`; verify the Pulumi Cloud preview on the PR shows only those additions
- [ ] 2.2 After merge, have the user run the prod `pulumi up`, and verify `gcloud --configuration=liverty-music artifacts repositories describe zitadel-login --location=asia-northeast2` succeeds

## 3. cloud-provisioning: patch, build and production wiring in one pull request (design D2, D3, D5, D6)

- [ ] 3.1 Add `zitadel-login/UPSTREAM_TAG` (`v4.20.0`) and `zitadel-login/patches/0001-*.patch` made with `git format-patch` against `zitadel/zitadel` at that tag, implementing D2: sign-up passkey only; no Password in the credential choice (IdP buttons kept); `notFound()` on `/register/password`, `/password/set` and `/password/change`; no reset request in the password form; `registerUser` refuses a `password`, and `resetPassword`, `changePassword`, `checkSessionAndSetPassword` and `setMyPassword` return an error without calling the API; `/password` sign-in untouched. Verify `git am` applies cleanly on a fresh checkout of the tag, one unit test per server action shows its refusal (the evidence for the design's `@spec-manual` "Password sent to the hosted login without its pages"), and `pnpm nx run @zitadel/login:test` passes
- [ ] 3.2 Add the GitHub Actions workflow of D3: on pull requests and `main` touching `zitadel-login/` and by `workflow_dispatch`, check out the tag, apply the patches, run the unit tests, `pnpm nx run @zitadel/login:build`, `docker build -f apps/login/Dockerfile apps/login` for `linux/amd64`, tag `zitadel-login:<UPSTREAM_TAG>-lm.<tree>` (`<tree>` = first 12 characters of `git rev-parse HEAD:zitadel-login`), and push through the existing `github-actions` service account unless the tag already exists; make the job a required check for pull requests touching `zitadel-login/`. Verify the pull request's run pushes the tag (`gcloud artifacts docker tags list`) and a re-run skips the push
- [ ] 3.3 Add the D6 check to `make lint-k8s`: `zitadel-login/UPSTREAM_TAG` equals `image.tag` in `k8s/namespaces/zitadel/base/values.yaml`, and `login.image.tag` in `k8s/namespaces/zitadel/overlays/prod/values.yaml` equals `<UPSTREAM_TAG>-lm.<tree>`; verify it fails when the tag pin, the base image tag or a patch changes without the matching prod tag
- [ ] 3.4 Set `login.image.repository` and `login.image.tag` in `k8s/namespaces/zitadel/overlays/prod/values.yaml`; verify the prod render shows the Artifact Registry image only on the Login V2 Deployment, the dev render keeps the upstream image, and `make lint-k8s` passes
- [ ] 3.5 Add the D6 upgrade procedure and the rollback note (rolling back re-opens password setup) to `docs/runbooks/zitadel-helm-chart.md`
- [ ] 3.6 After the pull request's image build has pushed the tag, merge, and verify ArgoCD is `Synced Healthy`, the `zitadel-api-login` pod runs the patched image with 0 restarts, and its log has no errors for 15 minutes

## 4. frontend: production checks of the closed pages

- [ ] 4.1 Add `e2e/prod/hosted-login-offers-no-password-setup.guest.spec.ts` covering fan hosted-login "Sign-up offers only a passkey", "Password pages opened by address" and "No password reset on the password page", and organizer hosted-login "Set-password page opened by address", each with its `@spec` annotation; verify it passes against production after 3.6
- [ ] 4.2 Verify `npm run test:e2e:prod` passes in full against production with the patched image

## 5. Production checks recorded as @spec-manual (design D7)

- [ ] 5.1 After 3.6, confirm the production test fans still sign in with their passwords without being sent to `/password/change` (design Risks: no `passwordChangeRequired`, no password age on the product org)
- [ ] 5.2 Re-invite the `e2e-test` Organizer's test member in production, confirm the credential choice shows Passkey and no Password and that enrolling the passkey ends at the organizer console, and record the date here; this is the evidence for the design's `@spec-manual` lines "Choosing a credential to set up offers no password" and "Invited person chooses a credential"

## 6. Unchanged login policy scenarios

- [ ] 6.1 Run the prod `pulumi preview` and confirm the product org and admin org login policies are unchanged; this is the evidence for the design's `@spec-manual` lines "Apply Strict Passkeys Policy on product org" and "Admin org isolation"

## 7. Residual risk check

- [ ] 7.1 Sign in to `https://auth.liverty-music.app/ui/console` as a production test fan and record whether the Console lets the fan set a password; if it does, open a follow-up issue for the Actions v2 request execution described in design Risks
