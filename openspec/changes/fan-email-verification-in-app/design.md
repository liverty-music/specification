## Context

See proposal.md - Why. This change builds on `identity-service` (an internal-only `identity` workload that holds every identity-provider key, with one listener and procedure allowlist per caller, and a NetworkPolicy per port). It is implemented only after that change is in production.

Facts checked on 2026-10-23 (zitadel v4.19.5 source, prod):
- **Who can verify an email**: User v2 `VerifyEmail` declares only `authenticated` (`user_service.proto:367-375`). `VerifyUserEmail` checks no permission; the code is the authorization (`internal/command/user_v2_email.go:192-213`).
- **Getting the code without ZITADEL's email**: v2 `SendEmailCode` supports `return_code` (`user_service.proto:2327-2329`), so ZITADEL sends nothing and returns the code. It always generates a new code. It does not check whether the address is already verified (`user_v2_email.go:169-190`, `273-283`).
- **The code**: 6 characters of upper-case letters and digits, valid 1 h (`cmd/defaults.yaml` `EmailVerificationCode`).
- **Why the email is English and "Zitadel"**:
  - Login UI v2 registers fans without `preferredLanguage` (`apps/login/src/lib/zitadel.ts:463-491`), and notifications fall back to the instance default (`en`) (`internal/notification/handlers/translator.go:17`).
  - ZITADEL's Japanese text is titled "Zitadel - メールアドレスの認証" and says "新しいメールアドレスが追加されました" (`internal/notification/static/i18n/ja.yaml:15-21`).
  - Pulumi provider 0.2.0 has no message-text or default-language resource.
- **Why the link is a dead end**: Login UI v2 `/verify/success` shows Continue only with a `requestId` (`apps/login/src/app/(login)/verify/success/page.tsx`), and an emailed link has none. Login UI does not auto-submit codes, to protect against link scanners (`NEXT_PUBLIC_AUTO_SUBMIT_CODE` off).
- **Who sends today**: the event consumer, for sign-up (`event.NewUserConsumer` → `EmailVerifier.SendVerification`) and for the resend (`UserUseCase.ReissueEmailVerification` → `ResendVerification`). After `identity-service`, both go through the identity service's `SendEmailVerification` and `ResendEmailVerification`.
- **Why the Settings badge is stale**: it reads `email_verified` from the ID token stored in localStorage (`frontend/src/routes/settings/settings-route.ts` `emailVerified`; `loadUserInfo: false` in `shared/services/auth-service.ts`).
- **Userinfo from the app**: the userinfo endpoint is `https://auth.liverty-music.app/oidc/v1/userinfo`. Its CORS preflight from `https://liverty-music.app` answers 204 with `allow-headers: authorization`. That the main access token is accepted there is not yet tested (task 4.1).
- **The existing pattern for a public, address-blind call** is `UserService.RequestPasskeyRecovery`: a public-procedure list on the fan server, an in-process limiter in the usecase, and a per-client interceptor keyed by client IP.

## Goals / Non-Goals

**Goals:**
- No identity-provider credential on the fan API. It reaches only the identity service's `VerifyEmail`.
- The verification email and screen speak the fan's language and the product's voice.

**Non-Goals:**
- Syncing the ZITADEL user's `preferredLanguage`. No ZITADEL-sent email to fans remains after this change.
- Organizer or admin email verification.

## Decisions

### D1. ZITADEL returns the code; the consumer emails it through Postmark

The identity service's `SendEmailVerification` and `ResendEmailVerification` call `SendEmailCode` with `return_code` and return `{email, code}`. Because `SendEmailCode` does not check verification, both first read `GetUserByID`:
- an already-verified address → FailedPrecondition, which keeps `User.ResendVerification`'s promise;
- an unknown identity → NotFound.

The consumer builds `https://liverty-music.app/verify-email?user=<User id>&code=<code>`. The origin is derived from the issuer, as for the passkey emails. The consumer sends the email with the existing Postmark sender in the User's `preferred_language` (`ja` when null), with ja/en templates in the style of the passkey registration email. The link and code are redacted from logs.

On the sign-up path the consumer handles `USER.created`, which carries the User, so it has the User id and language. The handler gains a User read by provider user id where it has only the identity.

Alternatives:

| Option | Rejected because |
|---|---|
| Set ZITADEL's `url_template` to the app route and keep ZITADEL's email | It fixes the dead end but not the language, the "Zitadel" name or the wording. |
| Sync `preferredLanguage` to ZITADEL | It fixes only the language, and it needs a write on every language change. |

### D2. The link carries our User id, not the provider user id

Our UUID keeps the identity provider's id out of URLs and email bodies. The fan API reads the User (`User.Get`) to get the provider user id. An unknown id and a wrong code both answer InvalidArgument (spec `usecase/user/verify-email`), so the link reveals nothing about which ids exist.

### D3. Public `UserService.VerifyEmail` on the fan API; the identity service verifies

- **proto**: `VerifyEmailRequest { UserId user_id; EmailVerificationCode code }` and an empty `VerifyEmailResponse`. `EmailVerificationCode` is a new wrapper of 1 to 32 characters. The call is added to the fan server's public-procedure list.
- **limits**:
  - The usecase limits attempts per User id in process: 5 per 60 min, counted before the read.
  - A per-client interceptor scoped to this procedure limits attempts by client IP: 10 per 60 min.
  - Like the passkey-recovery limiters, both are per pod.
- **verification**: the fan API calls `rpc.backend.user.v1.UserService.VerifyEmail` on a third identity listener, 9102.
  - That listener's allowlist holds only `VerifyEmail`.
  - NetworkPolicy `identity-ingress` gains TCP 9102 from `app=fan-api`.
  - `fan-api` gets `IDENTITY_SERVICE_URL`.
  - The identity service calls ZITADEL `VerifyEmail` with the `backend-app` key it already holds.
- **What a compromised fan API can do**: through 9102, only `VerifyEmail`. That needs a valid code, which only the address owner has.

### D4. The screen confirms on tap only

`/verify-email` is a public route (`data: { auth: false }`). It reads `user` and `code` from the query, shows "メールアドレスを確認する", and calls `VerifyEmail` only on that tap. This follows ZITADEL's own guard against link scanners, which open links and would use the code up.

- **Success**: say verified, and offer "アプリを開く" (the root route).
- **InvalidArgument**: say the link expired or was used, and point to Settings → 再送.
- **ResourceExhausted**: say to try later.
- **Network failure or Unavailable**: offer to try again.

The copy is drafted with a writer at implementation, as for the passkey screens.

### D5. The badge is read from userinfo on open and on return

Settings calls the userinfo endpoint with the current access token:
- on `attached`;
- on `visibilitychange` to visible.

It keeps `email_verified` in an observable on the auth service, which the badge and the resend action read. A failed read leaves the last known value.

Alternative: `signinSilent()` refreshes the token and its claims. Rejected: it rotates the refresh token, and the auth service deliberately serializes refreshes (`auth-retry-interceptor.ts`); a refresh on every focus would race. Userinfo is read-only.

If task 4.1 finds that ZITADEL rejects the main access token at userinfo, fall back to a refresh on Settings open only, and revise this decision.

## Risks / Trade-offs

- **[Risk]** Guessing a code for a known User id. 36^6 codes, a 1 h validity and 5 attempts per User per hour make a hit about 1 in 4×10^8. The limiters are per pod, so N pods multiply this by N. → Accepted at current scale; the same trade-off as passkey recovery. The identity provider's own `/verify` page already accepts codes without sign-in.
- **[Risk]** The one-time code travels from the identity service to the consumer over in-cluster h2c (as in `identity-service`). → Same mitigation: it is not logged, is single-use and expires in 1 h.
- **[Risk]** `identity-provider-credentials` (as rewritten by `identity-service`) says every other process reaches none of the identity service. → Its delta, which lets the fan API reach `VerifyEmail` only, is added after `identity-service` is archived (task 1.0). The two changes cannot both modify the same requirement at once.
- **[Trade-off]** Old links already sent by ZITADEL still open Login UI's page until they expire (1 h).

## Migration Plan

1. `identity-service` is in production and archived. Add the `identity-provider-credentials` delta here (task 1.0).
2. **specification**: `VerifyEmail` in `rpc/user/v1` and `rpc/backend/user/v1`, and `EmailVerificationCode`. Release.
3. **backend**: the identity listener 9102 and the `VerifyEmail` handler, `return_code` sending with the verified check, the consumer's Postmark email, and the public RPC with limiters. Release.
4. **cloud-provisioning**: port 9102 on Service `identity`, the NetworkPolicy rule from `app=fan-api`, and `IDENTITY_SERVICE_URL` on `fan-api`. Merge before the backend release is pinned. Old images ignore the variable.
5. **frontend**: `/verify-email` and the Settings badge refresh. Release.

**Rollback**: revert the consumer to the identity service's ZITADEL-sent path by reverting the backend release. ZITADEL's own email and link work again. The public RPC can stay.
