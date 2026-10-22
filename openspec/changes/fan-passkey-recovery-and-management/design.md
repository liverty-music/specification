## Context

See proposal.md - Why. Facts this design rests on (verified on 2026-10-21/22 unless marked):

- Fan passkeys live entirely in self-hosted ZITADEL v4.19.5 with the stock Login UI v2 (`/ui/v2/login`, RP ID `auth.liverty-music.app`). The platform stores only `users.provider_user_id`. Our code never calls WebAuthn.
- The WebAuthn ceremony can only run on the RP ID's origin. The fan app (`liverty-music.app`) cannot create a passkey for `auth.liverty-music.app`, and ZITADEL does not support Related Origin Requests. Every passkey creation therefore happens in Login UI v2.
- Login UI v2 `/passkey/set` (`apps/login/src/lib/server/passkeys.ts:48-154`):
  - Without a session, it accepts `userId` + `code` + `codeId` and registers a passkey with the code.
  - With a Login UI session cookie, it issues a code itself. The only check is that the session has a verified primary factor and has not expired (`enrollment-guard.ts:30-31`). There is no check on how recent the authentication was.
  - It names the passkey from the user agent (`passkeys.ts:165-175`, e.g. `Apple iPhone, iOS, Mobile Safari`).
- User v2 `CreatePasskeyRegistrationLink` requires `user.passkey.write` on the target user's organization, checked both by the interceptor and by the command (`internal/command/user_v2_passkey.go:140`, `permission_checks.go` `checkPermissionUpdateUserPasskey`).
  - Among org roles, only `ORG_OWNER` grants it (`cmd/defaults.yaml:1875`). `ORG_USER_MANAGER` does not (zitadel#12270, open).
  - Overriding `InternalAuthZ.RolePermissionMappings` replaces the whole list (`defaults.yaml:1585`).
  - The code is valid for 1 h (`defaults.yaml:1229-1231`). It is consumed when a registration starts (`user_v2_passkey.go:28-35`), so a cancelled browser prompt burns it (zitadel#12499).
- User v2 `ListPasskeys` and `RemovePasskey` accept the user's own token (`allowSelfManagement`) when it carries the `urn:zitadel:iam:org:project:id:zitadel:aud` scope.
  - `ListPasskeys` returns only id, state and name (`proto/zitadel/user/v2/user.proto:265-283`).
  - ZITADEL allows removing the last passkey.
- Prod ZITADEL answers CORS preflights from any origin. For `authorization,content-type` the reply carries `Access-Control-Allow-Origin` (Python preflight probe on 2026-10-22).
- Actions v2 event executions:
  - They POST `{aggregateID, aggregateType, resourceOwner, event_type, created_at, userID, event_payload}` (`internal/repository/execution/queue.go:52-78`).
  - A failed target call cancels the job and is never retried (`internal/execution/worker.go:38-57`).
  - The fan API already serves one such webhook, `/account-login-event`, with HMAC `ZITADEL-Signature` verification (`backend/internal/adapter/webhook/login_event_handler.go`).
- ZITADEL's default `PasswordlessRegistration` email reads "Zitadel - パスワードレスログインの追加". It has no "ignore if you did not request it" line (`internal/notification/static/i18n/ja.yaml:47-53`). Pulumi provider 0.2.0 has no message-text resource.
- The fan API holds the `backend-app` key (`ORG_USER_MANAGER`). The event consumer mounts the same key. The organizer-provisioner key lives only on `admin-console-api`.
- `users.email` is `UNIQUE` and case-sensitive, with a plain index (`schema.sql:13,509`).
- The organizer console already solves "email me a sign-in link without revealing whether I exist" (`OrganizerUseCase.SendSignInLinks`, `organizer_uc.go:670-705`): an in-process per-address limiter, a per-client interceptor limit, and the lookup and send detached from the request.

## Goals / Non-Goals

**Goals:**
- The fan API gains no new identity-provider privilege. The key that can issue registration links is never mounted on an internet-facing workload.
- Passkey list and removal run with the fan's own, freshly re-authenticated identity-provider token (ASVS 5.0 8.3.3 "originating subject's permissions").
- The recovery endpoint's answer and timing never depend on whether the address has an account.

**Non-Goals:**
- Storing passkey metadata (creation time, AAGUID, last use) on the platform.
- Closing Login UI v2's session-based `/passkey/set` path, which has no recency check. We cannot do this without forking the login app. Notifications and removal mitigate it.
- Moving the fan API's existing `backend-app` uses (account deletion, verification resend) off the fan API. That is the follow-up change.
- Organizer members' passkeys. Their identities are filtered out of notifications.

## Decisions

### D1. Recovery request: fan API answers, looks up later, announces only a user id

`UserService.RequestPasskeyRecovery(email)` is a public procedure. It is added to the fan server's public-procedure list alongside the existing unauthenticated ones.

The usecase mirrors `OrganizerUseCase.SendSignInLinks`:
- It applies an in-process per-address limiter (3 per 60 min, lower-cased key). An over-limit request succeeds silently.
- It answers immediately.
- On a context detached from the request (`context.WithoutCancel` plus a timeout), it runs `User.GetByEmail` and, on a hit, publishes `USER.passkey_recovery_requested` with `{user_id}`.

The per-client limit (10 per 60 min, keyed by client IP) is an interceptor scoped to this one procedure. It returns ResourceExhausted.

- **Why the lookup happens after answering**: answering before the read is what keeps timing from revealing whether an account exists. The organizer flow uses the same approach.
- **Why only `user_id` goes into the event**: the email never lands in JetStream, whose USER stream keeps messages for 7 days. This removes the retention question raised during exploration.
- Alternatives:
  - Publishing the raw email and resolving it in the consumer. Rejected: PII at rest in the stream, and no benefit.
  - Answering after the lookup with a constant delay. Rejected: fragile.
- The limiters are per pod, as on the organizer server. With N fan-api replicas the effective per-address limit is 3×N. This is accepted at current scale and is the same trade-off already made for organizer sign-in links.

### D2. Link issuance: dedicated `ORG_OWNER` service account on the event consumer, `returnCode`, our own email

The consumer handler `SendPasskeyRecoveryLink` does the following:
1. Reads the User.
2. Reads the identity with User v2 `GetUserByID`. If the email is not verified, it returns FailedPrecondition. If the user is unknown, it returns NotFound.
3. Calls `CreatePasskeyRegistrationLink` with `returnCode`.
4. Builds `https://<issuer host>/ui/v2/login/passkey/set?userId=<id>&code=<code>&codeId=<codeId>&organization=<product org id>`.
5. Emails the link through Postmark in the User's preferred language. The email states the 1-hour validity, the single-attempt rule and "ignore if you did not request this".

The operation `User.SendPasskeyRegistrationLink` is realized by an identity-provider client plus the existing Postmark sender. Both are injected only into the consumer.

**The privilege.** A new ZITADEL machine user, `fan-passkey-recovery`, holds `ORG_OWNER` on the product org. It has its own key in Secret Manager, synced into its own Kubernetes Secret, and is mounted only on `event-consumer`. The handler is the only code that loads that key.

| Option | Rejected because |
|---|---|
| Add `user.passkey.write` to `ORG_USER_MANAGER` by overriding `RolePermissionMappings` | We would copy roughly 560 lines of upstream defaults and drift silently on every upgrade (a missing permission for `IAM_LOGIN_CLIENT` would break login). |
| Grant `ORG_OWNER` to `backend-app` | That key is mounted on the internet-facing fan API. |
| Dedicated service account mounted on the fan API | Same exposure as granting `ORG_OWNER` to `backend-app`. |
| Wait for zitadel#12270 | No fix PR exists. |

**Why `returnCode` plus our own email, not `sendLink`.** ZITADEL's template names "Zitadel" and lacks the "ignore if not requested" text. It also picks the language from the identity's own setting rather than the platform's preferred language. Overriding the text would need a new Pulumi dynamic resource. Postmark templates already exist for order and resale emails. Trade-off: the one-time code passes through our process and Postmark. It is never logged, and the URL is redacted from logs.

**Retries.** A retried event issues a newer code. Earlier links stay valid until they expire or are used, because no invalidation of older codes was found. This is accepted: every link goes only to the verified address.

### D3. Passkey management: SPA calls ZITADEL with a separate, in-memory, re-authenticated token

Opening the Passkeys row starts a second OIDC authorization request:
- It uses its own oidc-client-ts `UserManager` with an `InMemoryWebStorage` user store and the callback route `/auth/passkeys-callback`.
- It requests `scope = openid urn:zitadel:iam:org:project:id:zitadel:aud` and `max_age = 300`. ZITADEL re-prompts for a passkey when the last authentication is older than 5 minutes.

The resulting token stays in memory while passkey management is open. It is discarded on leaving the screen and never refreshed (no `offline_access`).

With it, the SPA calls User v2 REST for the user id `sub`:
- `ListPasskeys`
- `RemovePasskey`

The main session's token keeps its current audience (the product project only).

- **Why not a backend RPC with `backend-app`**: that adds a new identity-provider dependency to the fan API, which the follow-up change is removing. It also acts with a service's permissions rather than the fan's (ASVS 5.0 8.3.3). With the fan's own token, a compromised fan API cannot list or remove anyone's passkeys.
- **Why not add the ZITADEL audience to the main token**: every fan-api request would then carry a token usable against ZITADEL, and an XSS anywhere in the app could use it for up to 30 minutes after any sign-in (OWASP Identity Propagation: "Do not widen token audiences").
- **Residual risk**: XSS while passkey management is open can use that token on the fan's own identity, for example to register a passkey through the self-management API. The token is short-lived and memory-only, and every addition is emailed (D6).
- **Requests**: REST/JSON (`/v2/users/{userId}/passkeys/...`) with only `authorization` and `content-type` headers, which match the verified CORS preflight. The exact REST paths are taken from the v4.19.5 API reference at implementation time.

### D4. Adding a passkey: full navigation to Login UI v2 `/passkey/set` with the fresh session

"Add a passkey on this device" works as follows:
1. The app sets a `sessionStorage` marker `returnTo=/settings/passkeys`.
2. It navigates to `https://<issuer host>/ui/v2/login/passkey/set?loginName=<email>&organization=<product org id>`.
3. The re-authentication in D3 has just refreshed the Login UI session on this browser, so the enrollment guard passes.
4. After registration, Login UI v2 asks for one assertion (zitadel#12885) and redirects to the login policy's `defaultRedirectUri`, the fan app root.
5. The root route consumes the marker and reopens passkey management. This re-runs D3, which is silent because `max_age` is satisfied.

Duplicate creation on the same provider is prevented by ZITADEL's `excludeCredentials` (`internal/webauthn/webauthn.go:60-79`).

- Alternative: have the backend issue a code (`returnCode`) for the signed-in fan and send them to `/passkey/set?userId&code&codeId`. Rejected: it puts the `user.passkey.write` key behind a fan-api request. It would also not close the session-based path, which stays reachable by URL anyway.

### D5. Last-passkey guard is client-side

The app disables removal when the list has one passkey. ZITADEL does not enforce this, and we cannot add the check server-side without proxying through the fan API (D3). A fan calling the API directly with their own token can only lock out themselves, and email recovery (D1, D2) restores access.

### D6. Notifications: two Actions v2 event executions → fan-API webhook → USER event → consumer → Postmark

Cloud-provisioning adds one Target `passkey-event-webhook`:
- `REST_CALL`, `PAYLOAD_TYPE_JSON`, `interruptOnError=false`, signing key stored as a secret.
- It points at the fan API's internal listener `/passkey-event`.

Two `ZitadelExecutionEvent`s point at it:
- `user.human.passwordless.token.verified`, a finished registration whose payload carries `webAuthNTokenName`.
- `user.human.passwordless.token.removed`.

The group `user.human.passwordless` is not used, because it also fires on every passkey sign-in (`check.succeeded`). `token.added` is not used, because it only marks an unfinished registration challenge.

The handler:
- Verifies the HMAC with `actions.ValidateRequestPayload`.
- Ignores events whose `resourceOwner` is not the product org.
- Publishes `USER.passkey_changed` with `{provider_user_id: aggregateID, kind, name, change_time: created_at}`.

The consumer handler `NotifyPasskeyChange` resolves the User by `provider_user_id` and sends the Postmark email.

- ZITADEL itself sends no email for these events (`internal/notification/handlers/user_notifier.go:25-80`).
- ZITADEL does not retry a failed target call. A webhook failure therefore loses that notification. We accept this: the publish goes to in-cluster NATS, and the loss is logged.
- Recovery-link use needs no third execution: it ends in `token.verified`, so the fan gets the added email.

### D7. No platform-side passkey metadata

Passkeys are shown by ZITADEL's name alone. Recording creation time and AAGUID from `token.verified` would add a table and columns whose only use is display. web.dev calls it "ideally", not required. We will revisit when a requirement needs it.

The Android UX guideline warns against device names for synced passkeys. We accept this for now because the name comes from Login UI v2.

### D8. `User.GetByEmail` is case-insensitive

The repository queries `WHERE lower(email) = lower($1)`. An Atlas migration adds `CREATE INDEX idx_users_email_lower ON users (lower(email))`.

The existing `UNIQUE (email)` is case-sensitive. If two rows match case-insensitively, the repository returns Internal and the usecase logs it and announces nothing. This is a safe failure. A read-only check of prod data during implementation confirms no such pair exists.

### D9. Login policy unchanged; spec corrected

`frontend.ts` keeps `userLogin: true` and `hidePasswordReset: true`. The fan hosted-login spec now states that local authentication must be on for passkeys, matching the organizer spec. The `TODO: Revert to false` comment in `frontend.ts` is reworded to point at this spec.

## Risks / Trade-offs

- **[Risk]** A cancelled or failed browser prompt on `/passkey/set` burns the one-time code (zitadel#12499). → The recovery screen offers a resend after 60 s, and the email says the link works for one attempt.
- **[Risk]** `/passkey/set` calls `navigator.credentials.create` on mount, without a user gesture (`register-passkey.tsx:200-205`). Safari may require transient activation. → Verify in prod on an iPhone with the owner's account. If it fails, file upstream and document the workaround (tap "Continue" if Login UI shows one).
- **[Risk]** ZITADEL leaves `residentKey` unset (zitadel#12942), so some authenticators may create non-discoverable or unsynced passkeys. → Login UI v2 asks for the login name first, so non-discoverable credentials still work. Track upstream.
- **[Risk]** Session-based `/passkey/set` adds a passkey for anyone holding an unlocked browser with a live Login UI session, with no recency check. → Every addition is emailed (D6), and passkeys can be removed (D3).
- **[Risk]** A compromised mailbox means a compromised account, because the link goes to the verified address. → This is inherent to email recovery. The added email notifies the fan, and NIST SP 800-63B-4 §4.2 notes this limit.
- **[Risk]** The `ORG_OWNER` key on `event-consumer` can change the whole product org if the consumer is compromised. The consumer has no inbound internet traffic, but it processes external data (Gemini results, web pages). → Only the recovery handler loads the key. A later split into a dedicated workload is possible without spec changes.
- **[Risk]** XSS while passkey management is open (D3). → The token is memory-only and discarded when passkey management closes. It is never refreshed, so it lives at most the 30-minute access-token lifetime. The fan app already ships a CSP (`frontend/index.html:15-`, `script-src 'self'` plus named hosts), and changes are emailed. Its `connect-src` already allows `https://*.liverty-music.app`, so the SPA's calls to the auth host need no CSP change.
- **[Trade-off]** Notifications are best-effort, because ZITADEL does not retry webhooks (D6).
- **[Trade-off]** Rate limiters are per pod (D1).

## Migration Plan

1. **specification**: add `UserService.RequestPasskeyRecovery` (`RequestPasskeyRecoveryRequest { UserEmail email }`, empty response). Merge, release, and wait for BSR gen.
2. **cloud-provisioning**:
   - Add the `fan-passkey-recovery` machine user (`ORG_OWNER` on the product org) and its key in Secret Manager.
   - Add an ExternalSecret and volume on `event-consumer`.
   - Add the passkey-event Target and the two event executions, plus the Target signing key secret for fan-api.
   - Add KEDA triggers for the two new JetStream consumers.
   - Merging auto-applies dev, which is stopped and unverifiable. Run prod `pulumi up` manually.
3. **backend**:
   - Migration for the `lower(email)` index.
   - Entity operations and usecases.
   - Public RPC with limiters.
   - `/passkey-event` webhook.
   - Consumer handlers and Postmark templates.
4. **frontend**:
   - `/passkey-recovery` screen.
   - Links on welcome and the Settings guest hero.
   - Passkeys section with the second OIDC flow and `/auth/passkeys-callback`.
   - Add-passkey navigation and return marker.

**Rollback**: hide the links and the Passkeys row (frontend), delete the two executions (cloud-provisioning), and unmount the recovery key. The public RPC can stay, because it only announces events.

**Verification in prod** (dev is stopped), with the owner's account:
- Request a link, register a passkey on a second device, then sign in.
- Check that the added and removed emails arrive.
- Remove a passkey and confirm it no longer signs in.
- Run an iPhone Safari check of `/passkey/set`.

## Open Questions

- The exact Login UI v2 behaviour after a code-based registration when there is no `requestId`: whether it lands on `/passkey` and then the `defaultRedirectUri`, or shows a success page. This only affects copy on the recovery email and screen, so it is settled during prod verification.
