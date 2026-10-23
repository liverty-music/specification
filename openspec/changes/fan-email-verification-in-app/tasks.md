## 1. Proto (specification)

- [ ] 1.0 After `identity-service` is archived, add the `components/infrastructure/backend/process/identity-provider-credentials` delta to this change: the fan API reaches only the identity service's verify operation (design Risks). Verify `openspec validate fan-email-verification-in-app --strict`
- [ ] 1.1 Add `UserService.VerifyEmail` to `rpc/user/v1/user_service.proto`: `VerifyEmailRequest { UserId user_id; EmailVerificationCode code }` with protovalidate, an empty response, and a doc comment saying it needs no sign-in and lists INVALID_ARGUMENT, RESOURCE_EXHAUSTED and UNAVAILABLE. Add the `EmailVerificationCode` wrapper (1-32 characters) and `VerifyEmail` (provider user id, code) on `rpc/internal/user/v1.UserService`. Change `SendEmailVerification` and `ResendEmailVerification` there to return `{email, code}` (design D1, D3). Verify `make check` and `buf breaking` in CI (apply `buf skip breaking` for the internal response change if reported)
- [ ] 1.2 Merge, publish a GitHub Release and confirm `buf-release.yml` succeeded

## 2. Identity provider operations (backend: identity service and entity)

- [ ] 2.1 Consume the released schema; verify `make check`
- [ ] 2.2 In the identity service:
  - make `SendEmailVerification` and `ResendEmailVerification` read `GetUserByID` first (verified → FailedPrecondition, unknown → NotFound), then call `SendEmailCode` with `return_code` and return the email and code (design D1);
  - add `VerifyEmail` calling ZITADEL `VerifyEmail`;
  - never log a code.

  Verify handler tests against a fake identity provider, including components/entity/user/verify-email "Valid code", "Code already used", "Code older than 1 hour", "Unknown identity"
- [ ] 2.3 Add listener 9102 whose allowlist holds only `VerifyEmail`; verify a test that it refuses `DeleteIdentity` and `SendEmailVerification` with PermissionDenied and allows `VerifyEmail`
- [ ] 2.4 Declare `User.VerifyEmail` on the entity interface. Implement it in the identity-service client, mapping InvalidArgument, NotFound and Unavailable; verify client contract tests for components/entity/user/verify-email (same four scenarios against a fake server)

## 3. Verification email and public RPC (backend)

- [ ] 3.1 Rework `User.SendVerification` and `User.ResendVerification` in the consumer:
  - take `{email, code}` from the identity service;
  - build `https://<fan web origin>/verify-email?user=<User id>&code=<code>`;
  - send through Postmark with ja/en templates (preferred language, `ja` when null; 1-hour validity; ignore-if-not-you) with the link and code redacted from logs;
  - give the sign-up handler a User read by provider user id.

  Verify contract tests for components/entity/user/send-verification "Unverified user", "Sending fails" and components/entity/user/resend-verification "Earlier code exists", "No earlier code", "Already verified", "Other failure" with the identity client and Postmark faked
- [ ] 3.2 Implement `UserUseCase.VerifyEmail`:
  - per-User-id in-process limiter, 5/60 min, counted before the read;
  - `User.Get`, then `User.VerifyEmail`;
  - NotFound and InvalidArgument map to InvalidArgument.

  Verify unit tests for components/usecase/user/verify-email "Link from the email", "Unknown User", "Expired or used link", "Identity provider down", "Sixth attempt for one User", "Eleventh attempt from one client" (the last with the interceptor of 3.3)
- [ ] 3.3 Add `VerifyEmail` to the user handler and the fan server's public-procedure list, with a per-client limiter interceptor scoped to it (10/60 min by client IP), and wire the fan API's identity-service client from `IDENTITY_SERVICE_URL`. Verify handler tests for components/adapter/fan/api/rpc/user "Not signed in", "Recovery request without sign-in", "Email verification without sign-in", "Link from the email", "Malformed link"
- [ ] 3.4 Merge, cut the backend Release after the push-path images are built

## 4. Screens (frontend)

- [ ] 4.1 Spike: from the signed-in fan app, call `https://auth.liverty-music.app/oidc/v1/userinfo` with the main access token and confirm it answers with `email_verified`; record the result in design D5 (if rejected, switch D5 to its fallback before 4.3)
- [ ] 4.2 Consume the released schema and build the `/verify-email` route (`auth: false`; confirm only on tap; outcomes per spec; ja/en copy drafted with a writer). Verify component tests for components/infrastructure/fan/web/route/verify-email "Opening the link", "Fan confirms", "Verified", "Expired or used link", "Too many attempts", "Network failure", "Broken link"
- [ ] 4.3 Read `email_verified` from userinfo on Settings open and on `visibilitychange` to visible, keeping the last value on failure (design D5). Verify tests for components/infrastructure/fan/web/route/settings "Verified on another device", "State cannot be read"
- [ ] 4.4 Merge and release; confirm `fan-web` rolled out in prod

## 5. Cluster (cloud-provisioning)

- [ ] 5.1 Add port 9102 to Service `identity`, the NetworkPolicy rule TCP 9102 from `app=fan-api`, and `IDENTITY_SERVICE_URL` on `fan-api`; merge before the backend release of 3.4 is pinned. Verify `kubectl kustomize` of the prod overlay and `make lint-k8s`

## 6. Prod verification (owner account; dev is stopped)

- [ ] 6.1 With the owner account, or a new account signed up for the check:
  - sign up and receive the verification email in Japanese, then confirm from the phone and see 認証済み on the laptop's Settings after returning to the tab;
  - open a link older than 1 hour and see it refused, then resend from Settings and verify with the new link;
  - confirm that `kubectl run` without `app=fan-api` cannot reach `identity:9102`.

  Record the evidence under each `@spec-manual` line below

@spec-manual stories/verify-email-address "Sign up, then verify on the phone" -- prod walk-through in task 6.1
@spec-manual stories/verify-email-address "Link expired" -- prod walk-through in task 6.1
