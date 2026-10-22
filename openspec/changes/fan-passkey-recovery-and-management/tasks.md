## 1. Proto (specification)

- [x] 1.1 Add `UserService.RequestPasskeyRecovery` (`RequestPasskeyRecoveryRequest { entity.v1.Email email }` with protovalidate required + email format + max 165, empty `RequestPasskeyRecoveryResponse`) to `proto/liverty_music/rpc/user/v1/user_service.proto` with doc comments stating it needs no sign-in and answers the same for every address; verify `buf lint` and `buf breaking` pass in CI
- [x] 1.2 Merge, publish a GitHub Release and confirm `buf-release.yml` succeeded (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)
- [x] 1.3 Add `entity/v1/passkey.proto` (`PasskeyId`, `PasskeyProviderName`, `Passkey { id, optional provider_name, create_time }`) and `rpc/passkey/v1/passkey_service.proto` (`PasskeyService.List(ListRequest {})` → `ListResponse { repeated Passkey passkeys }`, signed-in fan, errors UNAUTHENTICATED and NOT_FOUND; design D7); verify `buf lint` and `buf breaking` pass in CI
- [x] 1.4 Merge, publish a second GitHub Release and confirm `buf-release.yml` succeeded

## 2. Identity provider and cluster configuration (cloud-provisioning)

- [x] 2.1 Add the `fan-passkey-recovery` machine user with `ORG_OWNER` on the product org and a JSON key stored in Secret Manager (design D2), following `machine-user.ts`; verify `pulumi preview` for prod shows only the new user, membership, key and secret
- [x] 2.2 Add an ExternalSecret and volume mounting that key on `event-consumer` only (not `fan-api`), with an env var for its path; verify `kubectl kustomize` of the prod overlay shows the mount on `event-consumer` and none on `fan-api`
- [x] 2.3 Add the `passkey-event-webhook` Target (`REST_CALL`, `PAYLOAD_TYPE_JSON`, `interruptOnError=false`) pointing at the fan API internal listener `/passkey-event`, and two `ZitadelExecutionEvent`s on `user.human.passwordless.token.verified` and `user.human.passwordless.token.removed` (design D6) in `actions-v2.ts`; store the Target signing key for fan-api like the login-event key; verify `pulumi preview`
- [x] 2.4 Add KEDA `nats-jetstream` triggers for the new consumers `send-passkey-recovery-link`, `notify-passkey-change` and `record-passkey-change` on the USER stream; verify `kubectl kustomize` output
- [x] 2.5 Reword the `userLogin: true` TODO comment in `src/zitadel/components/frontend.ts` to cite the corrected hosted-login spec (local authentication must stay on for passkeys); verify `make check`
- [ ] 2.6 Run prod `pulumi up` manually after merge and confirm the machine user, Target and both executions exist (Zitadel console or `ListExecutions`), quoting the output

## 3. Entity operations (backend)

- [x] 3.1 Add an Atlas migration creating `idx_users_email_lower ON users (lower(email))`, run a read-only prod query confirming no two `users.email` values collide case-insensitively (design D8), and verify the migration lint passes (`atlas migrate lint` needs Atlas Pro locally; verified by the Atlas CI and Schema Lint checks on backend#675)
- [x] 3.2 Declare `User.GetByEmail` on the user repository interface and implement it with `lower(email) = lower($1)` (Internal on more than one match); verify contract tests for components/entity/user/get-by-email "Registered address", "Different letter case", "Unregistered address", "Empty address"
- [x] 3.3 Implement `User.SendPasskeyRegistrationLink` with an identity-provider client using the `fan-passkey-recovery` key (GetUserByID for the verified email, `CreatePasskeyRegistrationLink` with `returnCode`, link built from the issuer and product org id) plus a Postmark sender with ja/en templates (1-hour validity, single attempt, ignore if not requested) and the URL redacted from logs; verify contract tests for components/entity/user/send-passkey-registration-link "Verified address", "Unverified address", "Identity removed" against a fake identity provider
- [x] 3.4 Implement `User.SendPasskeyChangeEmail` as a Postmark sender with ja/en templates (kind, optional name, time in Japan time, link to `/passkey-recovery` and to Settings passkeys); verify contract tests for components/entity/user/send-passkey-change-email "Passkey added", "Passkey removed", "Mail unavailable"
- [x] 3.5 Add an Atlas migration creating the `passkeys` table (design D7) and implement `Passkey.Create` (idempotent on provider passkey id), `Passkey.Delete` and `Passkey.ListByUser` on a passkey repository; verify the migration lint (Atlas CI and Schema Lint checks on backend#675) and contract tests for components/entity/passkey/create "New passkey", "Same passkey again", "Unknown User", components/entity/passkey/delete "Recorded passkey", "Never recorded", components/entity/passkey/list-by-user "Two recorded passkeys", "Nothing recorded"
- [x] 3.6 Vendor the names-only AAGUID map with its upstream commit and a `make` refresh target (design D11) and derive the Passkey provider name from it; verify unit tests for components/entity/passkey "Known provider", "Provider not revealed or not listed"

## 4. Usecases and events (backend)

- [x] 4.1 Add the `USER.passkey_recovery_requested` (`{user_id}`) and `USER.passkey_changed` (`{provider_user_id, provider_passkey_id, kind, name, aaguid, change_time}`) subjects and payload types with json tags in `internal/entity/event_data.go`; verify `make check`
- [x] 4.2 Implement `UserUseCase.RequestPasskeyRecovery` (per-address in-process limiter 3/60 min, detached lookup and publish, per-client limit surfaced as ResourceExhausted) following `OrganizerUseCase.SendSignInLinks`; verify unit tests for components/usecase/user/request-passkey-recovery "Address of a fan account", "Address with no account", "Store unavailable", "Fourth request for one address", "Eleventh request from one client"
- [x] 4.3 Implement `UserUseCase.SendPasskeyRecoveryLink` and register the `send-passkey-recovery-link` consumer handler; verify unit tests for components/usecase/user/send-passkey-recovery-link "Fan with a verified address", "Unverified address", "Account deleted since the request", "Mail service down"
- [x] 4.4 Implement `UserUseCase.NotifyPasskeyChange` and register the `notify-passkey-change` consumer handler; verify unit tests for components/usecase/user/notify-passkey-change "Passkey added on a new device", "Passkey added through a recovery link", "Passkey removed", "Identity with no account", "Mail unavailable"
- [x] 4.5 Wire DI so only the consumer builds the identity-provider recovery client (missing key path → consumer starts with the handler disabled and logs it, fan API never loads it); verify a DI test and `make check`
- [x] 4.6 Implement `PasskeyUseCase.RecordChange` and register the `record-passkey-change` consumer handler (retry while no User matches, give up after 10 minutes from `change_time`; design D7); verify unit tests for components/usecase/passkey/record-change "Passkey added", "Passkey removed", "Change announced twice", "Store unavailable", "Account created after the passkey", "Identity that never becomes an account"
- [x] 4.7 Implement `PasskeyUseCase.List`; verify unit tests for components/usecase/passkey/list "Fan with recorded passkeys", "Fan with no record"

## 5. Adapters (backend)

- [x] 5.1 Add `RequestPasskeyRecovery` to the user handler and the fan server's public-procedure list, with the per-client limiter interceptor scoped to that procedure (10/60 min by client IP); verify handler tests for components/adapter/fan/api/rpc/user "Recovery request without sign-in", "Not signed in", "Well-formed address", "Malformed address", "Client over its limit"
- [x] 5.2 Add the `/passkey-event` webhook on the internal listener (HMAC verification, product-org filter on `resourceOwner`, `token.verified` → added with `webAuthNTokenName`, `webAuthNTokenId` and the decoded `aaguid`, `token.removed` → removed with `webAuthNTokenId`, publish failure → 500 and log); verify handler tests for components/adapter/fan/api/webhook/passkey-events "Valid signature", "Forged notice", "Passkey registered", "Passkey removed", "Organizer identity", "Announcement fails"
- [x] 5.3 After the second release, consume the schema and add the `PasskeyService` handler on the fan server (signed-in, resolves the caller, calls `PasskeyUseCase.List`); verify handler tests for components/adapter/fan/api/rpc/passkey "Fan lists their passkeys", "Not signed in", "No account"

## 6. Screens (frontend)

- [x] 6.1 Consume the released schema (`consume-proto-release` skill) and swap placeholder types; verify `make check`
- [x] 6.2 Build the `/passkey-recovery` route (email form, uniform success message, 60-second resend countdown, ResourceExhausted and network error states, ja/en i18n); verify component tests for components/infrastructure/fan/web/route/passkey-recovery "Fan sends their address", "Address with no account", "Malformed address", "Resend after 60 seconds", "Too many requests", "Network failure"
- [x] 6.3 Add the "can't sign in" link below `[Log In]` on welcome and in the Settings guest hero; verify tests for components/infrastructure/fan/web/route/welcome "Link below Log In", "Link opens the recovery screen" and components/infrastructure/fan/web/route/settings "Guest opens sign-in help from Settings"
- [x] 6.4 Implement the passkey-management auth flow (second oidc-client-ts `UserManager` with in-memory store, `/auth/passkeys-callback`, scope `openid urn:zitadel:iam:org:project:id:zitadel:aud`, `max_age=300`, token discarded on leave; design D3); verify tests for components/infrastructure/fan/web/route/settings "Recent sign-in", "Older sign-in", "Re-opening after leaving" with the OIDC client mocked
- [x] 6.5 Implement the Passkeys row and management view (list via User v2 REST ListPasskeys, removal with confirmation and passkey-manager note, last-passkey guard, error states, add-on-this-device navigation to `/ui/v2/login/passkey/set` with the `returnTo` marker consumed at the root route; design D4, D5); verify tests for components/infrastructure/fan/web/route/settings "Two passkeys", "Add a passkey on this device", "Remove a passkey", "Last passkey", "Removal fails"
- [x] 6.6 After the second release, show each passkey's provider name and date from `PasskeyService.List`, joined to the identity provider's list by id (the id match is checked in prod in task 7.1; design D7); verify tests for components/infrastructure/fan/web/route/settings "Recorded passkey", "Passkey without a record"
- [x] 6.7 Build the add-passkey prompt (per-device `localStorage` record set on sign-up, on add from Settings or the prompt and on "already has one"; "Later"/dismiss hides it for 30 days; shown after a Log In only; design D10); verify component tests for components/infrastructure/fan/web/global/add-passkey-prompt "Log In with another device's passkey", "Device that already has the record", "Later chosen recently", "Later chosen long ago", "Create on this device", "Already has one", "Dismissed"

## 7. Prod verification (owner account; dev is stopped)

- [ ] 7.1 With the owner account in prod: request a recovery link, open it on a second device (including an iPhone with Safari, to confirm `/passkey/set` works without an extra tap - design Risks), register a passkey, sign in, then add and remove a passkey from Settings, Log In on a laptop with the phone by QR code and accept the add-passkey prompt, and check that Settings shows provider and date for the new passkeys (which also confirms the ListPasskeys id equals the announced provider passkey id and that the webhook payload field names match); confirm the added and removed emails arrive and the removed passkey no longer signs in; record the evidence in this file under each `@spec-manual` line below

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
@spec-manual stories/manage-passkeys "QR sign-in, then a passkey on the laptop" -- prod walk-through in task 7.1
