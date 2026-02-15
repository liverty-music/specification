## Context

Zitadel serves as the identity provider (IdP) for the Liverty Music platform via OIDC/PKCE. When a user signs up, Zitadel creates the identity record, but the application database (`users` table) remains empty. The backend currently validates JWTs and extracts the `sub` claim but has no mechanism to provision local user records.

Current state:
- Frontend distinguishes signup (`prompt=create`) from login in `AuthService`
- Backend auth interceptor validates JWT and injects `sub` into context
- `users` table exists with UUIDv7 `id`, `email`, `name`, etc. but no Zitadel identity link
- `UserService` has `Create` and `Get` RPCs but no identity-aware provisioning

## Goals / Non-Goals

**Goals:**
- Provision a local user record immediately after Zitadel signup
- Link Zitadel identity (`sub` claim) to the local user record via `external_id`
- Keep the solution simple — minimal moving parts for MVP
- Ensure idempotency — calling provisioning multiple times for the same user is safe

**Non-Goals:**
- Zitadel Actions v2 Webhook integration (future phase)
- Syncing profile updates from Zitadel to local DB (future phase)
- Backend interceptor-based auto-provisioning fallback (future phase)
- Admin-created user sync (future phase)

## Decisions

### Decision 1: Client-side provisioning via OIDC `state`

**Choice**: Frontend detects signup via `state: { isRegistration: true }` passed through the OIDC flow, then calls `Create` RPC in the auth callback.

**Alternatives considered**:
- **Zitadel Actions v2 Webhook**: Push-based, real-time sync. More robust but requires hosting a webhook endpoint, signature verification, and fallback for missed events. Deferred to future phase.
- **Backend interceptor auto-provisioning**: Every authenticated request checks if user exists. Reliable fallback but adds DB query to every request and mixes auth concerns with provisioning.
- **Event API polling**: Batch reconciliation via Zitadel Event Store. Good for catch-up but not real-time, requires checkpoint management.

**Rationale**: The frontend already controls the signup vs login distinction. Passing `state` through OIDC is a standard pattern supported by `oidc-client-ts`. This requires zero additional infrastructure and integrates naturally into the existing callback flow.

### Decision 2: `external_id` column (UUID type) instead of reusing Zitadel `sub` as primary key

**Choice**: Add a new `external_id UUID UNIQUE NOT NULL` column to `users`, keeping the existing UUIDv7 `id` as primary key. Zitadel's `sub` claim is a UUID, so UUID type is appropriate.

**Alternatives considered**:
- **Use Zitadel `sub` as `users.id`**: Simpler mapping but couples the primary key to an external system. Internal references (foreign keys, logs) would use an opaque external ID.
- **TEXT type**: More flexible but loses UUID validation at the database level. Since Zitadel `sub` is always a UUID, using the proper type is better.

**Rationale**: Decoupling internal identity from external identity is a standard practice. The application owns its primary key format (UUIDv7), and `external_id` serves as the lookup index for identity resolution. UUID type provides type safety and compact storage.

### Decision 3: Use existing `Get` and `Create` RPCs (no new RPC)

**Choice**: Extend the existing `Create` RPC to accept `external_id` and `email` as parameters. The frontend calls `Create` on signup. Idempotency is handled via the database UNIQUE constraint on `external_id` — if the user already exists, `Create` returns `ALREADY_EXISTS`.

**Alternatives considered**:
- **New `GetOrCreate` RPC**: Single idempotent call. However, this introduces a non-standard RPC pattern and mixes read/write semantics. The existing `Get`/`Create` separation is cleaner and follows resource-oriented API design (Google AIP).

**Rationale**: Keeping the API surface minimal and following existing conventions. The frontend knows it's a registration flow, so calling `Create` is semantically correct. The `ALREADY_EXISTS` error on retry is a clear, expected response.

### Decision 4: Extract user profile from JWT claims

**Choice**: Use claims already present in the JWT/ID token (`email`, `name`, `locale`) rather than calling Zitadel's UserInfo endpoint.

**Rationale**: The Zitadel OIDC app is configured with `userInfoAssertion: true`, so the ID token already contains profile claims. This avoids an extra network round-trip.

## Risks / Trade-offs

**[Risk] User signs up but closes browser before callback completes** → The user exists in Zitadel but not in the local DB. On next login, the frontend won't call `Create` because `state.isRegistration` is only set during `register()`. Mitigation: Accept this gap for MVP. Future mitigation: add backend interceptor fallback or Zitadel Actions v2 Webhook.

**[Risk] `state` parameter is client-controlled and not tamper-proof** → A malicious client could call `Create` with arbitrary data. Mitigation: The `Create` RPC must validate the JWT and use the authenticated `sub` claim as the source of truth for `external_id`, not client-provided data.

**[Risk] Duplicate `Create` calls** → Network retry or double-click could cause a second `Create` for the same `external_id`. Mitigation: Database UNIQUE constraint on `external_id` ensures the second call returns `ALREADY_EXISTS`. The frontend handles this gracefully.

**[Trade-off] No profile update sync** → If a user changes their email or name in Zitadel, the local DB will be stale. Accepted for MVP — can be addressed later via Zitadel Actions v2 or periodic reconciliation.

## Architecture

```
┌──────────┐   register()    ┌──────────┐   OIDC callback   ┌──────────┐
│  User    │ ──────────────► │ Zitadel  │ ────────────────► │ Frontend │
│          │  prompt=create  │          │   code + state    │          │
└──────────┘                 └──────────┘                   └────┬─────┘
                                                                 │
                                                    state.isRegistration?
                                                          ┌──────┴──────┐
                                                          │ yes         │ no
                                                          ▼             ▼
                                                   Create RPC        redirect home
                                                   (external_id,
                                                    email, name)
                                                          │
                                                          ▼
                                                   ┌──────────┐
                                                   │ Backend  │
                                                   │ Create   │
                                                   └────┬─────┘
                                                        │
                                                   INSERT user
                                                   (external_id UNIQUE)
                                                        │
                                                        ▼
                                                   ┌──────────┐
                                                   │ Postgres │
                                                   │  users   │
                                                   └──────────┘
```
