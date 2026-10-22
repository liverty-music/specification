## 1. Proto (specification)

- [ ] 1.1 Add `UserService.RequestPasskeyRecovery` (`RequestPasskeyRecoveryRequest { UserEmail email }` with protovalidate required + email format + max 165, empty `RequestPasskeyRecoveryResponse`) to `proto/liverty_music/rpc/user/v1/user_service.proto` with doc comments stating it needs no sign-in and answers the same for every address; verify `buf lint` and `buf breaking` pass in CI
- [ ] 1.2 Merge, publish a GitHub Release and confirm `buf-release.yml` succeeded (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Identity provider and cluster configuration (cloud-provisioning)

- [ ] 2.1 Add the `fan-passkey-recovery` machine user with `ORG_OWNER` on the product org and a JSON key stored in Secret Manager (design D2), following `machine-user.ts`; verify `pulumi preview` for prod shows only the new user, membership, key and secret
- [ ] 2.2 Add an ExternalSecret and volume mounting that key on `event-consumer` only (not `fan-api`), with an env var for its path; verify `kubectl kustomize` of the prod overlay shows the mount on `event-consumer` and none on `fan-api`
- [ ] 2.3 Add the `passkey-event-webhook` Target (`REST_CALL`, `PAYLOAD_TYPE_JSON`, `interruptOnError=false`) pointing at the fan API internal listener `/passkey-event`, and two `ZitadelExecutionEvent`s on `user.human.passwordless.token.verified` and `user.human.passwordless.token.removed` (design D6) in `actions-v2.ts`; store the Target signing key for fan-api like the login-event key; verify `pulumi preview`
- [ ] 2.4 Add KEDA `nats-jetstream` triggers for the new consumers `send-passkey-recovery-link` and `notify-passkey-change` on the USER stream; verify `kubectl kustomize` output
- [ ] 2.5 Reword the `userLogin: true` TODO comment in `src/zitadel/components/frontend.ts` to cite the corrected hosted-login spec (local authentication must stay on for passkeys); verify `make check`
- [ ] 2.6 Run prod `pulumi up` manually after merge and confirm the machine user, Target and both executions exist (Zitadel console or `ListExecutions`), quoting the output

## 3. Entity operations (backend)

- [ ] 3.1 Add an Atlas migration creating `idx_users_email_lower ON users (lower(email))`, run a read-only prod query confirming no two `users.email` values collide case-insensitively (design D8), and verify `atlas migrate lint` passes
- [ ] 3.2 Declare `User.GetByEmail` on the user repository interface and implement it with `lower(email) = lower($1)` (Internal on more than one match); verify contract tests for components/entity/user/get-by-email "Registered address", "Different letter case", "Unregistered address", "Empty address"
- [ ] 3.3 Implement `User.SendPasskeyRegistrationLink` with an identity-provider client using the `fan-passkey-recovery` key (GetUserByID for the verified email, `CreatePasskeyRegistrationLink` with `returnCode`, link built from the issuer and product org id) plus a Postmark sender with ja/en templates (1-hour validity, single attempt, ignore if not requested) and the URL redacted from logs; verify contract tests for components/entity/user/send-passkey-registration-link "Verified address", "Unverified address", "Identity removed" against a fake identity provider
- [ ] 3.4 Implement `User.SendPasskeyChangeEmail` as a Postmark sender with ja/en templates (kind, optional name, time in Japan time, link to `/passkey-recovery` and to Settings passkeys); verify contract tests for components/entity/user/send-passkey-change-email "Passkey added", "Passkey removed", "Mail unavailable"

## 4. Usecases and events (backend)

- [ ] 4.1 Add the `USER.passkey_recovery_requested` (`{user_id}`) and `USER.passkey_changed` (`{provider_user_id, kind, name, change_time}`) subjects and payload types with json tags in `internal/entity/event_data.go`; verify `make check`
- [ ] 4.2 Implement `UserUseCase.RequestPasskeyRecovery` (per-address in-process limiter 3/60 min, detached lookup and publish, per-client limit surfaced as ResourceExhausted) following `OrganizerUseCase.SendSignInLinks`; verify unit tests for components/usecase/user/request-passkey-recovery "Address of a fan account", "Address with no account", "Store unavailable", "Fourth request for one address", "Eleventh request from one client"
- [ ] 4.3 Implement `UserUseCase.SendPasskeyRecoveryLink` and register the `send-passkey-recovery-link` consumer handler; verify unit tests for components/usecase/user/send-passkey-recovery-link "Fan with a verified address", "Unverified address", "Account deleted since the request", "Mail service down"
- [ ] 4.4 Implement `UserUseCase.NotifyPasskeyChange` and register the `notify-passkey-change` consumer handler; verify unit tests for components/usecase/user/notify-passkey-change "Passkey added on a new device", "Passkey added through a recovery link", "Passkey removed", "Identity with no account", "Mail unavailable"
- [ ] 4.5 Wire DI so only the consumer builds the identity-provider recovery client (missing key path → consumer starts with the handler disabled and logs it, fan API never loads it); verify a DI test and `make check`

## 5. Adapters (backend)

- [ ] 5.1 Add `RequestPasskeyRecovery` to the user handler and the fan server's public-procedure list, with the per-client limiter interceptor scoped to that procedure (10/60 min by client IP); verify handler tests for components/adapter/fan/api/rpc/user "Recovery request without sign-in", "Not signed in", "Well-formed address", "Malformed address", "Client over its limit"
- [ ] 5.2 Add the `/passkey-event` webhook on the internal listener (HMAC verification, product-org filter on `resourceOwner`, `token.verified` → added with `webAuthNTokenName`, `token.removed` → removed, publish failure → 500 and log); verify handler tests for components/adapter/fan/api/webhook/passkey-events "Valid signature", "Forged notice", "Passkey registered", "Passkey removed", "Organizer identity", "Announcement fails"

## 6. Screens (frontend)

- [ ] 6.1 Consume the released schema (`consume-proto-release` skill) and swap placeholder types; verify `make check`
- [ ] 6.2 Build the `/passkey-recovery` route (email form, uniform success message, 60-second resend countdown, ResourceExhausted and network error states, ja/en i18n); verify component tests for components/infrastructure/fan/web/route/passkey-recovery "Fan sends their address", "Address with no account", "Malformed address", "Resend after 60 seconds", "Too many requests", "Network failure"
- [ ] 6.3 Add the "can't sign in" link below `[Log In]` on welcome and in the Settings guest hero; verify tests for components/infrastructure/fan/web/route/welcome "Link below Log In", "Link opens the recovery screen" and components/infrastructure/fan/web/route/settings "Guest opens sign-in help from Settings"
- [ ] 6.4 Implement the passkey-management auth flow (second oidc-client-ts `UserManager` with in-memory store, `/auth/passkeys-callback`, scope `openid urn:zitadel:iam:org:project:id:zitadel:aud`, `max_age=300`, token discarded on leave; design D3); verify tests for components/infrastructure/fan/web/route/settings "Recent sign-in", "Older sign-in", "Re-opening after leaving" with the OIDC client mocked
- [ ] 6.5 Implement the Passkeys row and management view (list via User v2 REST ListPasskeys, removal with confirmation and passkey-manager note, last-passkey guard, error states, add-on-this-device navigation to `/ui/v2/login/passkey/set` with the `returnTo` marker consumed at the root route; design D4, D5); verify tests for components/infrastructure/fan/web/route/settings "Two passkeys", "Add a passkey on this device", "Remove a passkey", "Last passkey", "Removal fails"

## 7. Prod verification (owner account; dev is stopped)

- [ ] 7.1 With the owner account in prod: request a recovery link, open it on a second device (including an iPhone with Safari, to confirm `/passkey/set` works without an extra tap - design Risks), register a passkey, sign in, then add and remove a passkey from Settings; confirm the added and removed emails arrive and the removed passkey no longer signs in; record the evidence in this file under each `@spec-manual` line below

@spec-manual components/infrastructure/fan/web/global/hosted-login "Apply Strict Passkeys Policy on product org" -- prod `pulumi preview` shows the product org login policy unchanged (userLogin true, passwordless allowed, hidePasswordReset true, external IdP off); task 2.6
@spec-manual components/infrastructure/fan/web/global/hosted-login "Admin org isolation" -- unchanged behaviour; prod `pulumi preview` shows no change to the admin org policy; task 2.6
@spec-manual components/infrastructure/fan/web/global/hosted-login "Fan lost every passkey" -- prod walk-through in task 7.1
@spec-manual components/infrastructure/fan/web/global/hosted-login "Valid link" -- prod walk-through in task 7.1
@spec-manual components/infrastructure/fan/web/global/hosted-login "Cancelled passkey prompt" -- prod walk-through in task 7.1 (cancel the prompt once, confirm the link no longer works)
@spec-manual components/infrastructure/fan/web/global/hosted-login "Second device" -- prod walk-through in task 7.1
@spec-manual components/infrastructure/fan/web/global/hosted-login "Same provider again" -- prod walk-through in task 7.1 (add twice on one device, confirm one passkey)
@spec-manual components/entity/user/send-passkey-registration-link "Link opened on a new device" -- prod walk-through in task 7.1
@spec-manual components/entity/user/send-passkey-registration-link "Link older than 1 hour" -- prod walk-through in task 7.1 (open a link after 61 minutes)
@spec-manual components/entity/user/send-passkey-registration-link "Link used twice" -- prod walk-through in task 7.1
@spec-manual stories/recover-sign-in-after-losing-passkeys "Lost phone, new phone" -- prod walk-through in task 7.1
@spec-manual stories/recover-sign-in-after-losing-passkeys "Someone else types the fan's address" -- prod walk-through in task 7.1 (request from a second browser, confirm the same message and that only the owner mailbox receives the link)
@spec-manual stories/recover-sign-in-after-losing-passkeys "Link expired" -- prod walk-through in task 7.1
@spec-manual stories/manage-passkeys "Phone to laptop" -- prod walk-through in task 7.1
@spec-manual stories/manage-passkeys "Unrecognized passkey" -- prod walk-through in task 7.1
@spec-manual stories/manage-passkeys "Only one passkey" -- prod walk-through in task 7.1
