## Context

The `self-hosted-zitadel` cutover went live 2026-04-30. The cutover smoke-test passed and dev runs entirely on `auth.dev.liverty-music.app`. During the cutover incident chain, four operational gaps emerged that did not exist in the original proposal:

1. **Dead webhook handler.** The original `auto-verify-email` Action was supposed to set `email.is_verified = true` on incoming `AddHumanUser` requests via an Actions v2 `request:*` Execution. Empirically this turned out to be impossible because Zitadel v4 `request:*` Executions REPLACE the entire request body with the webhook response (zitadel/zitadel#9748), so a webhook returning `{email: {is_verified: true}}` stripped Profile / Phone / Username and broke `AddHumanUser` validation. cloud-provisioning#215 removed the Zitadel-side Target + Execution, but the backend handler was not removed in the same PR — it sits at `internal/adapter/webhook/auto_verify_email_handler.go` receiving zero traffic.

2. **`ResendEmailVerification` regression.** The backend RPC currently calls Zitadel's User Service v2 `_resend_code` endpoint. This endpoint **only resends an existing code**; if no code was ever generated (e.g., SMTP was inactive at sign-up time, which was the §13.16 incident path), the call fails with `Code is empty (EMAIL-5w5ilin4yt)` and the frontend Settings page surfaces a vague "Failed to send verification email" error to the user. The Management v1 `_resend_verification` endpoint generates a new code AND sends the email — this is what users actually mean by "resend".

3. **Manual SMTP activation.** `@pulumiverse/zitadel.SmtpConfig` (v0.2.0) provisions a `SmtpConfig` resource but does NOT call the separate `_activate` admin endpoint that Zitadel v4 requires before SMTP traffic flows. The cutover required a one-shot `curl POST /admin/v1/smtp/{id}/_activate` to unstick first-sign-up email verification. Every Zitadel rebuild silently re-introduces the same gap until the operator remembers.

4. **Missing Pulumi Dynamic Resource tests.** During the cutover chain, two implementation bugs in the Dynamic Resource module each cost a deploy cycle: PR #211 (PATCH→POST on Target update — Zitadel's API expects POST for both create and update on Actions v2) and PR #212 (`targets: [{target: id}]` vs. `targets: [id]` — the proto shape is `string[]`, not `[]Target`). Both bugs would have been caught by lifecycle tests. The original proposal §4.5 acknowledged this gap and deferred it; this change closes it.

## Goals / Non-Goals

**Goals:**

- Eliminate the `/auto-verify-email` dead code from the backend so the webhook surface matches the actual Zitadel-side configuration (one route: `/pre-access-token`).
- Make `ResendEmailVerification` work in the post-cutover state where users were created with no initial verification code.
- Move the SMTP `_activate` step from operator memory to Pulumi-managed declarative state.
- Lock in the wire-level Dynamic Resource contract via fast-feedback unit tests so the next addition (e.g., the `pulumi-deploy-safeguards` deploy hook, or the §18.10 Cloud-tenant teardown) cannot regress on the same shape mistakes.

**Non-Goals:**

- Rewriting `auto-verify-email` to actually work (option (c) from §18.4: full `AddHumanUser` payload reconstruction in the webhook). Decided in §18.4 to accept Zitadel's default OTP step.
- Touching Zitadel v1 Action infrastructure (none remains; the v1→v2 migration was completed in the cutover).
- Adding integration tests against a live Zitadel — out of scope; mocked-HTTP fast tests cover the contract that broke during the cutover.
- Frontend changes. The Settings page Resend button stays as-is; the change is fully server-side.
- Bundling §18.6.2 Cloud Monitoring alert (separate concern, not warning-tier).

## Decisions

### D1. Use Zitadel Management v1 `_resend_verification` endpoint, not v2 `_resend_code`

The v2 User Service `_resend_code` is intentionally narrow: it resends an _existing_ code without re-generating one, useful when a user requests another delivery of the code they already have. The v1 Management `_resend_verification` is broader: it generates a fresh code and sends the email. The user-facing "Resend verification email" button on the Settings page maps to the broader semantic — users don't think in terms of "is there an existing code". v1 it is.

The risk of using a v1 endpoint: Zitadel could deprecate v1 in a future major. Mitigation: v1 Management is the most-used and most-stable surface in Zitadel; deprecation, when it comes, will be telegraphed years out. We will catch it in the upgrade test cycle and re-target as needed.

**Alternative considered:** Pre-create the verification code at sign-up time (so v2 `_resend_code` always has something to resend). Rejected — requires a separate post-`AddHumanUser` API call in the sign-up flow, adds a failure mode to sign-up itself, and doesn't match the user-intent semantic.

### D2. Implement `ZitadelSmtpActivation` as a Pulumi Dynamic Resource, not as a Pulumi Command resource

We already have three Dynamic Resources for the same kind of "Pulumi-managed Zitadel REST API call" pattern: `ZitadelTarget`, `ZitadelExecutionFunction`, `ZitadelExecutionRequest`. Adding a fourth keeps the pattern consistent and lets the new test suite cover all four uniformly.

**Alternative considered:** Use Pulumi `command.local.Command` to fire `curl _activate` after `SmtpConfig` is up. Rejected — `command.local.Command` runs on the deployer's machine (or Pulumi Cloud Deployments runner), not against the Zitadel API auth context the Dynamic Resource already has, and would require re-implementing the OAuth `client_credentials` token exchange ad hoc. The Dynamic Resource extends `getAccessToken(jwtProfileJson)` from `dynamic/zitadel-api-client.ts`, so it gets auth for free.

The `ZitadelSmtpActivation` resource tracks no state — it's a pure side-effect call. The `create` handler fires `_activate`; the `update` handler is a no-op (re-activating an already-active SMTP returns 200 from Zitadel, and there's no "deactivate" semantic in the API surface we care about); the `delete` handler is also a no-op (deleting the activation record doesn't deactivate the upstream SMTP). The resource exists to make the Pulumi state graph see "activation happened" as a tracked fact, not to maintain bidirectional state.

### D3. Test framework: vitest with `vi.fn()` HTTP mocking, not `nock` or a record/replay tool

`cloud-provisioning` is a TypeScript project; `vitest` is the natural pick (faster than Jest, native ESM, the project's other TypeScript code already uses vitest where tests exist). Mocking is via `vi.fn()` on the `fetch` API — the Dynamic Resources call `fetch` directly (no library wrapping), so mocking at that boundary captures the wire-level contract that the §13.5/§13.6 incidents broke.

**Alternative considered:** Use `nock` for HTTP-level interception. Rejected — `nock` is a Node-only library that intercepts at the `http`/`https` module level; we'd need to verify it works with `fetch` in the Pulumi Node runtime, and it adds a dependency for no functional gain over `vi.fn`.

**Alternative considered:** Record/replay against a live Zitadel sandbox. Rejected — the goal is to catch shape mistakes (PATCH vs POST, array vs object) at PR-time on every developer's machine. Record/replay couples test runs to a live tenant.

### D4. Test fixtures encode the v4 contract that broke during cutover

The four-case scaffold below applies to **stateful** Dynamic Resources — those that map to a Zitadel API resource readable via `GET /<path>/{id}`. The current three (`ZitadelTarget`, `ZitadelExecutionFunction`, `ZitadelExecutionRequest`) all qualify. Test cases:

- `create()` MUST issue a `POST` to the documented path, with the request body shape that Zitadel v4 actually accepts (e.g., `targets: string[]` for Execution, NOT `targets: [{target: string}]`).
- `update()` MUST issue a `POST` (NOT `PATCH`) — Zitadel v4 returns `405 Method Not Allowed` on PATCH for Actions v2 resources.
- `delete()` MUST issue a `DELETE` to `<path>/{id}`.
- `read()` MUST tolerate the `404 Not Found` case (resource was deleted out-of-band) by returning `null` rather than throwing.

These four cases collectively encode the §13.5 / §13.6 incident shapes plus the standard Pulumi Dynamic Resource lifecycle expectations.

**Carve-out for side-effect-only resources.** `ZitadelSmtpActivation` (the new resource introduced in PR-B2) intentionally diverges from this scaffold: activation is a one-shot side effect with no individually addressable `_activate` resource at the API surface — there is no `GET /admin/v1/smtp/{id}/_activation` endpoint to read, no separate `_deactivate` endpoint, and no inputs other than `smtpConfigId` to update. Its `update()` / `read()` / `delete()` handlers are no-ops by design (per D2's "side-effect-only resource" framing and the spec's idempotency scenario), so its test scaffold is narrower: assert that `create()` POSTs and that the other three lifecycle methods make ZERO HTTP calls. Future Dynamic Resources added to the module SHOULD inherit the four-case scaffold unless they are also side-effect-only, in which case they SHOULD inherit the narrower scaffold and call out the divergence in their tasks document (as PR-B2 does in §4.1 and §4.4).

### D5. Backend RPC change is a 1-line endpoint swap, not an architectural rework

`internal/infrastructure/zitadel/email_verifier.go::ResendVerification` builds an HTTP request to a Zitadel API path string. The change is the path string + the HTTP method (the v1 Management endpoint is also a POST, so method doesn't change) + minor JSON body adjustments if any. The RPC handler signature, the upstream RPC contract, the JWT-derived authorization check, the rate-limit, and the error-mapping all stay identical.

This is intentional: the regression was a wrong-endpoint choice, not a flawed architecture. Re-architecting would risk introducing new bugs to fix a one-line bug.

### D6. Order the four sub-deliverables by blast radius

The implementation order in tasks.md is:

1. **PR-A1**: Delete dead `/auto-verify-email` handler. Pure subtraction; smallest risk.
2. **PR-A2**: Switch `ResendEmailVerification` endpoint. User-visible bug fix, but a single-line endpoint change with existing tests.
3. **PR-B1**: Add Dynamic Resource test suite (Tests for the existing three resources only — no new functionality). Locks in the contract before PR-B2 introduces the fourth Dynamic Resource.
4. **PR-B2**: Add `ZitadelSmtpActivation` Dynamic Resource + wire into `smtp.ts` + extend the test suite from PR-B1 with the new resource. This requires a `pulumi up` against the dev stack.

PR-B1 lands before PR-B2 so the test scaffold exists when the new resource is added, avoiding "tests retrofit later" debt.

## Risks / Trade-offs

- **[Risk] Zitadel deprecates Management v1 after we adopt it for Resend.** → Mitigation: D1 rationale. When deprecation is announced, we re-target via a follow-up; in the meantime the user-visible bug is fixed.
- **[Risk] `_activate` returns a non-200 success code or a Zitadel-specific "already active" error that the Dynamic Resource mis-classifies as failure.** → Mitigation: empirically verified during the manual cutover step; PR-B2 test fixtures encode the actual response shape, not the assumed shape.
- **[Risk] Deleting the orphan handler breaks an unrelated test or Wire DI binding.** → Mitigation: `make check` in backend runs the full test suite + Wire codegen; failures show up at PR time.
- **[Risk] The Dynamic Resource test suite breaks every time Zitadel changes the Actions v2 wire format.** → Tradeoff: this is the design intent. Tests SHOULD break when the upstream API changes shape; that signal is exactly what we lacked during cutover.
- **[Trade-off] `ZitadelSmtpActivation` is a side-effect-only resource with no state to read.** → The Pulumi state graph records that activation happened, but cannot detect drift if an operator manually `_deactivate`-s SMTP out-of-band. Acceptable for dev; if drift becomes a recurring problem, add a `read()` handler that GETs `/admin/v1/smtp/{id}` and checks the `state` field.

## Migration Plan

This change has no migration in the database / schema sense. Steps:

1. PR-A1 (backend) merges → `make check` passes → ArgoCD rolls out new image. The `/auto-verify-email` route 404s afterwards; nothing was calling it, so no downstream breakage.
2. PR-A2 (backend) merges → backend pod rolls. The Settings page "Resend verification email" button starts working for users created during the SMTP-inactive window.
3. PR-B1 (cloud-provisioning) merges → CI runs vitest; no infra change.
4. PR-B2 (cloud-provisioning) merges → Pulumi Cloud Deployments runs `pulumi up`. The first run creates the `ZitadelSmtpActivation` resource and fires `_activate`; subsequent runs are no-ops.

Rollback: each PR is a single revert. PR-B2 rollback removes the Dynamic Resource from state but does not deactivate SMTP (that's idempotent and harmless).

## Open Questions

- **Q1**: Does the Management v1 `_resend_verification` endpoint require any specific scope on the backend's MachineUser token beyond what `ResendEmailVerification` already uses? → To verify during PR-A2 implementation. Mitigation: empirically the cutover smoke test fired this endpoint with the existing `backend-app` MachineUser token and got a 200, so the scope set is sufficient.
- **Q2**: When `self-hosted-zitadel` is archived, do this change's `identity-management` deltas still apply cleanly? → Both this change and `self-hosted-zitadel` modify the same requirement. Resolution: rebase this change onto archived `self-hosted-zitadel` so the requirement exists in main specs at the time the delta lands.
