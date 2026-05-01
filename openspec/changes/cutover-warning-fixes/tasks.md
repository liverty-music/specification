## 1. PR-A1 — Backend: delete orphan `/auto-verify-email` handler

Goal: cleanly remove the dead webhook handler that lost its caller in cloud-provisioning#215. Keep `:9090` listener and `/pre-access-token` handler unchanged.

- [ ] 1.1 Delete `backend/internal/adapter/webhook/auto_verify_email_handler.go`
- [ ] 1.2 Delete `backend/internal/adapter/webhook/auto_verify_email_handler_test.go`
- [ ] 1.3 Drop the `/auto-verify-email` route registration from the `:9090` mux setup (`internal/server/webhook.go` or equivalent — find via `grep -rn "auto-verify-email"`)
- [ ] 1.4 Drop the `auto_verify_email_handler` provider from the Wire DI module (`internal/di/`); regenerate Wire if needed
- [ ] 1.5 Remove any orphaned imports / type references that the deletions surface
- [ ] 1.6 Run `make check` in `backend/` — lint + tests must pass
- [ ] 1.7 Open backend PR titled `cleanup(webhook): remove orphan /auto-verify-email handler`; CI green; merge after review

## 2. PR-A2 — Backend: switch `ResendEmailVerification` to Management v1 endpoint

Goal: fix the user-visible "Failed to send verification email" bug for users created during the SMTP-inactive cutover window.

- [ ] 2.1 Locate `ResendVerification` in `backend/internal/infrastructure/zitadel/email_verifier.go` (or wherever the v2 path string is constructed)
- [ ] 2.2 Change the endpoint path from `/v2/users/{externalId}/email/_resend_code` (or whatever the current v2 path is) to `/management/v1/users/{externalId}/email/_resend_verification`
- [ ] 2.3 Adjust the request body shape if the v1 endpoint requires a different JSON envelope; verify against Zitadel docs and the smoke-test trace from §13.16
- [ ] 2.4 Update existing unit tests that assert the URL path / request method to match the new endpoint
- [ ] 2.5 Add a unit test covering the "no prior code exists" case — the endpoint should succeed (mocked 200) without the `Code is empty (EMAIL-5w5ilin4yt)` upstream error
- [ ] 2.6 Run `make check` in `backend/` — lint + tests pass
- [ ] 2.7 Open backend PR titled `fix(zitadel): use Management v1 _resend_verification for ResendEmailVerification`; verify in dev after rollout that Settings page button works for the SMTP-inactive-window users; merge

## 3. PR-B1 — cloud-provisioning: Pulumi Dynamic Resource lifecycle test suite

Goal: lock in the Zitadel v4 wire-level contract (POST for both create and update; `targets: string[]` not `[]Target`; 404 tolerance on read) that the §13.5 / §13.6 incidents broke. Tests cover the existing three resources only; the new `ZitadelSmtpActivation` resource lands in PR-B2 and gets the same scaffold by copy-edit.

- [ ] 3.1 Add `vitest` as a `devDependency` in `cloud-provisioning/package.json` if not already present; ensure `package.json` `scripts.test` invokes it
- [ ] 3.2 Create `cloud-provisioning/src/zitadel/dynamic/__tests__/zitadel-api-client.test.ts` with a `vi.fn()` fetch mock + a `getAccessToken` happy-path test that asserts the `client_credentials` grant URL and request body
- [ ] 3.3 Create `__tests__/target.test.ts` covering `ZitadelTarget`:
  - `create()` issues `POST /v2/actions/targets` with the expected body shape
  - `update()` issues `POST` (NOT `PATCH`) — encodes the §13.5 incident shape
  - `delete()` issues `DELETE /v2/actions/targets/{id}`
  - `read()` returns `null` on `404` rather than throwing
- [ ] 3.4 Create `__tests__/execution.test.ts` covering `ZitadelExecutionFunction` and `ZitadelExecutionRequest`:
  - `create()` body MUST be `{ targets: ["<id>"] }` (string array) — encodes the §13.6 incident shape
  - same `update`-uses-`POST`, `delete`-issues-`DELETE`, `read`-tolerates-`404` cases
- [ ] 3.5 Run `npm test` (or whatever script vitest is wired to) in `cloud-provisioning/`; all green
- [ ] 3.6 Run `make check` — lint + tests pass; CI mirrors local
- [ ] 3.7 Open cloud-provisioning PR titled `test(zitadel): add Pulumi Dynamic Resource lifecycle tests`; merge

## 4. PR-B2 — cloud-provisioning: `ZitadelSmtpActivation` Dynamic Resource + auto-activate `SmtpConfig`

Goal: make Zitadel SMTP activation declarative so every rebuild does not silently break first-sign-up email verification.

- [ ] 4.1 Create `cloud-provisioning/src/zitadel/dynamic/smtp-activation.ts` exporting `ZitadelSmtpActivation` extending `pulumi.dynamic.Resource`. Lifecycle handlers (note: this resource intentionally diverges from the Target / Execution four-case lifecycle because activation is a one-shot side effect with no readable or updatable state at the Zitadel API surface):
  - `create(inputs.smtpConfigId)`: get OAuth token via `getAccessToken`, then `POST /admin/v1/smtp/{id}/_activate`. Return an outputs object containing `smtpConfigId` and `activatedAt` (timestamp).
  - `update()`: **no-op**. Do NOT re-fire `_activate`; do NOT mutate `activatedAt`. Pulumi handles input-diff replace-vs-update internally; an `update` call here means inputs other than `smtpConfigId` changed (none exist in the input shape today), so there is nothing to do. Aligns with `design.md` D2 and the spec scenario "Activation is idempotent across re-apply."
  - `delete()`: no-op (no `_deactivate` semantic in our use-case).
  - `read()`: no-op returning current outputs unchanged. Activation is a side effect with no separate readable state at the Zitadel API surface (one would GET `SmtpConfig`, which is owned by a different resource). Drift detection is explicitly deferred per `design.md` D2 Risks.
- [ ] 4.2 Export `ZitadelSmtpActivation` from `src/zitadel/dynamic/index.ts`
- [ ] 4.3 In `src/zitadel/components/smtp.ts`, instantiate `ZitadelSmtpActivation` with `smtpConfigId: smtpConfig.id` and `dependsOn: [smtpConfig]`
- [ ] 4.4 Add `__tests__/smtp-activation.test.ts` (new file). The test scaffold is **deliberately narrower** than the four-case scaffold from PR-B1 because of the resource's side-effect-only semantics:
  - `create()` issues `POST /admin/v1/smtp/{id}/_activate` with the expected request shape; mock 200 response satisfies the call
  - `create()` succeeds when the upstream returns the "already active" response shape (idempotency on first apply against an out-of-band-activated SMTP)
  - `update()` makes ZERO HTTP requests (no `fetch` invocation); asserts the mock was not called
  - `delete()` makes ZERO HTTP requests
  - `read()` makes ZERO HTTP requests and returns current outputs unchanged
- [ ] 4.5 Run `make check`; all tests + lint green
- [ ] 4.6 Run `pulumi preview --stack dev` from a clean checkout; expected diff: `+ create urn:...:ZitadelSmtpActivation:smtp-activation` and zero replacements / deletes
- [ ] 4.7 Open cloud-provisioning PR titled `feat(zitadel): auto-activate SmtpConfig via Pulumi Dynamic Resource`; verify the `pulumi preview` output is attached to the PR description; merge after approval
- [ ] 4.8 Post-merge: confirm Pulumi Cloud Deployment auto-runs `pulumi up`; SMTP state in dev Zitadel remains `SMTP_CONFIG_ACTIVE` (already active from the manual `curl` step). The first apply executes `create()` (which calls `_activate`; Zitadel returns the "already active" response and the operation succeeds idempotently). Subsequent applies execute `update()` as a no-op with zero HTTP traffic.
- [ ] 4.9 Confirm via Zitadel admin API: `GET /admin/v1/smtp/{id}` returns `state: SMTP_CONFIG_ACTIVE`

## 5. Verification

- [ ] 5.1 Run `/opsx:verify cutover-warning-fixes` after PR-A1, PR-A2, PR-B1, PR-B2 are all merged
- [ ] 5.2 Confirm the §18.1, §18.2, §18.3, §4.5 / §18.9 follow-up checkboxes in `self-hosted-zitadel/tasks.md` are all checkable; tick them
- [ ] 5.3 Run `/opsx:archive cutover-warning-fixes` to fold deltas into main `openspec/specs/`
