## Context

Users register via Passkey on Zitadel's Hosted Login UI. Currently, a Zitadel Action (`autoVerifyEmail`) marks every user's email as verified at creation time, so no verification email is ever sent. Testing confirmed that removing this Action does NOT block the Passkey OIDC flow — users sign up normally with `email: not verified`. However, Zitadel does not auto-send verification emails for Passkey registrations (unlike password-based flows), so the backend must explicitly trigger them.

The backend currently has no Zitadel API client — it only validates JWTs via `lestrrat-go/jwx`. The `zitadel-go/v3` SDK and a Machine User service account are needed for API calls.

## Goals / Non-Goals

**Goals:**
- Users receive a verification email after signing up
- Email verification does not block the signup/login flow
- Users can resend the verification email from the Settings page
- `email_verified` JWT claim reflects real verification state
- Backend authenticates to Zitadel API via Private Key JWT (asymmetric, secure for future ticket sales)

**Non-Goals:**
- Custom verification UI — Zitadel's hosted verification page handles code entry
- Custom `urlTemplate` for verification links — use Zitadel's default
- Feature gating based on `email_verified` status (future work for ticket sales)
- Email change flow — only initial verification for now

## Decisions

### 1. Remove `autoVerifyEmail` Action

The `autoVerifyEmail` Action and its `PRE_CREATION` trigger are deleted from cloud-provisioning. The `auto-verify-email.js` script file is also removed. Users are created with `email: not verified`.

The `addEmailClaim` Action and its `PRE_ACCESS_TOKEN_CREATION` trigger remain unchanged. The `email_verified` claim will now reflect the real Zitadel verification state.

**Alternative considered:** Keep the Action but add a POST_CREATION trigger to re-send verification. Rejected because this creates contradictory state (verified then immediately unverified) and adds unnecessary complexity.

### 2. Private Key JWT for Machine User authentication

A Zitadel Machine User is provisioned via Pulumi with a Private Key JWT credential. The private key JSON file is stored in GCP Secret Manager and mounted into the backend pod via External Secrets Operator (ESO).

**Why Private Key JWT over Client Credentials:** Asymmetric authentication — the private key never leaves the backend, Zitadel only stores the public key. If Zitadel's database is compromised, the credential cannot be used to impersonate the service account. This is the recommended approach for services handling financial transactions (future ticket sales).

**Why not PAT:** Static tokens cannot be scoped, have no expiry negotiation, and are a single point of compromise.

### 3. NATS `USER.created` event for async verification trigger

User creation in `UserUseCase.Create()` publishes a `USER.created` event to NATS JetStream after successful database persistence. The `userUseCase` struct receives a `message.Publisher` (Watermill) injection, following the existing pattern in `concertCreationUseCase`, `concertUseCase`, and `artistUseCase`. A subject constant `entity.SubjectUserCreated` is defined in `internal/entity/`.

A consumer subscribes to this event and calls `POST /v2/users/{externalId}/email/send` via the `zitadel-go` SDK.

**Why NATS over synchronous call in UseCase:**
- Email verification failure should never block user creation
- JetStream provides automatic retry with backoff on transient failures
- Follows existing patterns (CONCERT, VENUE, ARTIST streams)
- Clear separation of concerns — user creation logic stays focused

**Stream configuration** follows the existing pattern: `USER.*` subjects, 7-day retention, file storage, 2-minute deduplication window.

### 4. Resend verification via backend RPC proxy

A new RPC method `ResendEmailVerification` is added to the existing `UserService`. The handler extracts the authenticated user's `external_id` from JWT claims and calls `POST /v2/users/{externalId}/email/resend` via the `zitadel-go` SDK.

**Why proxy through backend instead of frontend calling Zitadel directly:**
- Frontend does not have Zitadel Admin API credentials
- Backend can enforce rate limiting and authorization
- Consistent with the pattern of all external API calls going through backend

### 5. Zitadel API client as infrastructure component

The `zitadel-go` client is initialized in both DI entrypoints:
- `internal/di/provider.go` (API server) — for the `ResendEmailVerification` RPC handler
- `internal/di/consumer.go` (event consumer) — for the `USER.created` event handler

It uses `client.DefaultServiceUserAuthentication()` with the private key JSON file path. The client is injected into the consumer and the UserService handler via an `EmailVerifier` interface defined in `internal/usecase/`.

**Configuration additions to `pkg/config/config.go`:**
- `ZitadelMachineKeyPath` — path to the machine key JSON file (mounted from Secret Manager via `ZITADEL_MACHINE_KEY_PATH`). Added to both `ServerConfig` and `ConsumerConfig`.
- Zitadel domain reuses existing `JWT.Issuer` (no new field needed)

## Risks / Trade-offs

**[Risk] Machine User key rotation** → Private keys should be rotated periodically. Mitigation: Pulumi can generate a new key and update Secret Manager; ESO syncs to the pod. The old key is revoked in Zitadel. This is a manual but infrequent operation.

**[Risk] SMTP delivery failure is silent to the user** → If Postmark fails to deliver, the user simply doesn't receive the email. Mitigation: Resend button on Settings page. Future: monitor Postmark delivery webhooks.

**[Risk] Zitadel rate limits on email/send** → High signup volume could hit rate limits. Mitigation: NATS consumer processes events sequentially with backoff. Current user volumes are low.

**[Risk] `email_verified` claim changes mid-session** → After a user verifies their email, the JWT `email_verified` claim updates on the next token refresh, not immediately. Mitigation: Acceptable UX — the Settings page can re-fetch verification status from the backend if needed.
