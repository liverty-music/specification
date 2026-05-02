## Why

The `self-hosted-zitadel` cutover landed end-to-end on 2026-04-30 (smoke test passed, sign-up + login working against `auth.dev.liverty-music.app`). Subsequent `/opsx:verify` surfaced four post-cutover hygiene items that, individually, are too small to warrant their own change but collectively block archive readiness:

- A backend webhook handler that no longer has a Zitadel-side caller (dead code surface).
- A user-visible bug in the `ResendEmailVerification` RPC that surfaces when SMTP was inactive at sign-up time (incident-path regression from the cutover).
- A manual operational step (SMTP activation via `curl`) that breaks every fresh Zitadel rebuild silently until the operator remembers to run it.
- A test gap in the Pulumi Dynamic Resource module that directly cost ~3 hours of incident response during the cutover (PR #211 PATCH→POST and #212 array-of-strings shape mistakes would have been caught by lifecycle tests).

These four items share one archive-readiness goal and ship in a single batch over ~1 week. Bundling avoids splitting nearly-identical post-cutover commit footers across four PRs.

## What Changes

- **Delete the orphan `/auto-verify-email` backend webhook handler** (`internal/adapter/webhook/auto_verify_email_handler.go` + tests + DI wiring + `:9090` route registration). The Zitadel-side Target + Execution were removed in cloud-provisioning#215 during the cutover incident chain; the handler is now dead code with no caller. The `:9090` listener and `/pre-access-token` handler remain unchanged.
- **Switch `liverty_music.rpc.user.v1.UserService/ResendEmailVerification` from Zitadel v2 `_resend_code` to Zitadel v1 Management `POST /management/v1/users/{userId}/email/_resend_verification`**. The v2 endpoint only resends an EXISTING code; if SMTP was inactive at sign-up time (the §13.16 incident path), no code was ever generated, and the call fails with `Code is empty (EMAIL-5w5ilin4yt)`. The v1 endpoint generates a fresh code AND sends the email — this is the contract users actually expect from "resend." Verified to work via direct API call during the cutover smoke test.
- **Add a `ZitadelSmtpActivation` Pulumi Dynamic Resource** at `cloud-provisioning/src/zitadel/dynamic/smtp-activation.ts` that calls `POST /admin/v1/smtp/{id}/_activate` after `SmtpConfig` creation, mirroring the existing `ZitadelTarget` / `ZitadelExecutionFunction` pattern. Wire it into `src/zitadel/components/smtp.ts`. Idempotent on retries (re-activating an already-active SMTP returns success). Without this, every Zitadel rebuild silently fails first-sign-up email verification until an operator fires the `_activate` `curl` manually.
- **Add a `vitest`-based mocked-HTTP test suite** for the lifecycle of `ZitadelTarget`, `ZitadelExecutionFunction`, `ZitadelExecutionRequest`, and the new `ZitadelSmtpActivation`. Fixtures SHALL reflect the actual Zitadel v4 REST API contract (POST for both create AND update, JSON shape with `targets: string[]` rather than `targets: {target: string}[]`). The PR #211/#212 incident chain would have been caught by these tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `email-verification`: The "Resend verification email via RPC" requirement is updated to specify the Zitadel Management v1 `_resend_verification` endpoint (rather than v2 `_resend_code`) and gains a scenario covering the "no prior code exists" case, which the v2 endpoint does not handle.
- `identity-management`: The "SMTP Configuration Must Be Activated After Creation" requirement (introduced by `self-hosted-zitadel`) gains a scenario codifying that activation occurs declaratively via the `ZitadelSmtpActivation` Pulumi Dynamic Resource, not via a manual operator step. The requirement's intent is unchanged — the new scenario constrains the implementation contract.

## Impact

**Affected repositories**

- `backend/`:
  - `internal/adapter/webhook/auto_verify_email_handler.go` + tests + Wire DI module references (deleted).
  - `internal/infrastructure/zitadel/email_verifier.go` (or wherever `ResendVerification` lives) — endpoint change from v2 to v1 Management.
  - `internal/server/webhook.go` (or equivalent) — drop the `:9090` route registration for `/auto-verify-email`.
- `cloud-provisioning/`:
  - `src/zitadel/dynamic/smtp-activation.ts` (new) — Dynamic Resource implementation.
  - `src/zitadel/dynamic/index.ts` — export the new class.
  - `src/zitadel/components/smtp.ts` — instantiate the activation resource after `SmtpConfig`.
  - `src/zitadel/dynamic/__tests__/*.test.ts` (new) — mocked-HTTP lifecycle tests for all four Dynamic Resources.
  - `package.json` — add `vitest` as a dev dependency if not already present.

**Affected systems**

- Dev `auth.dev.liverty-music.app` Zitadel instance: the next `pulumi up` after this change SHALL transition `SmtpConfig` from `INACTIVE` to `ACTIVE` declaratively. No data change.
- Backend `:9090` webhook listener: shrinks from two routes to one (`/pre-access-token` only). External attack surface unchanged (still cluster-internal `ClusterIP` only).
- Frontend Settings page "Resend verification email" button: starts working in the post-cutover state where the user signed up while SMTP was inactive.

**Dependencies**

- None on external services. The Zitadel v1 Management API is documented as long-stable (no deprecation horizon at v4) per the Zitadel maintainer reference linked from §18.2.
- Soft dependency on `self-hosted-zitadel` archiving (or its spec deltas merging) so that the `identity-management` "SMTP Configuration" requirement exists in main specs before this change's delta modifies it. If `self-hosted-zitadel` is still active when this change archives, the modification SHALL be re-targeted at the in-flight delta rather than at main specs.

**Out of scope (already covered or deferred)**

- §18.9.1 Pulumi state-recovery runbook → existing `pulumi-deploy-safeguards` change stub.
- §18.7 K8s deploy rename → existing `k8s-naming-cleanup` change stub.
- §18.8 GSM secret rename → existing `rename-zitadel-machine-key-secret` change stub.
- §18.10 Cloud tenant decommission → existing `archive-zitadel-cloud-tenant` change stub.
- §18.4 auto-verify-email behavior → decided (keep default OTP); no implementation work.
- §18.5 Playwright password test user → tracked outside openspec at `liverty-music/frontend#345`.
- §18.6 Zitadel hang monitoring (alert) → not warning-tier; passive observation continues until cooldown ends ~2026-05-14.
