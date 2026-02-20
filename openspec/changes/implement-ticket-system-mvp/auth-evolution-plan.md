# Authentication Evolution Plan: Option A → Option C

> Created: 2026-02-20
> Context: [design.md Decision 4](design.md#decision-4-authentication-via-zitadel-passkey-rp--safe-address-from-usersid)

## Overview

The MVP starts with **Option A** (Zitadel as the sole WebAuthn Relying Party, using its hosted login UI). This document defines the migration path to **Option C** (Zitadel for existing auth + self-hosted go-webauthn RP for ticket-specific Passkey auth), triggered when Zitadel's Passkey limitations become blocking.

## Current State (Option A — MVP)

```
User ──OIDC──▶ Zitadel (hosted login UI) ──JWT──▶ Go Backend
                 │                                    │
                 ├─ Passkey registration              ├─ JWT validation (jwx)
                 ├─ Passkey authentication            ├─ users.id → Safe address
                 └─ Session management                └─ Ticket / Entry handlers
```

- Authentication: Zitadel hosted login UI with Passkey support
- Frontend: `oidc-client-ts` → Zitadel OIDC → JWT
- Backend: `lestrrat-go/jwx/v2` validates JWT; `users.external_id` maps to Zitadel `sub` claim
- Safe address: Derived from `users.id` (UUIDv7), not from credential or external_id

## Triggers for Migration

Migrate to Option C when **any** of the following become true:

| Trigger | Zitadel Reference | Impact |
|---|---|---|
| Custom Login UI required AND Issue #8282 unresolved | [Issue #8282](https://github.com/zitadel/zitadel/issues/8282) | Cannot use Passkey on custom domain |
| Conditional UI (Passkey autofill) required | [Discussion #8867](https://github.com/zitadel/zitadel/discussions/8867) | Cannot implement passwordless autofill UX |
| Credential public key needed for on-chain operations | ListPasskeys API limitation | Cannot derive on-chain identity from credential |
| Domain migration required without re-registering Passkeys | Passkeys concept docs | All existing Passkeys invalidated |

## Target State (Option C)

```
User ──OIDC──▶ Zitadel (existing users, OIDC)
  │                │
  │                └─ JWT (existing auth, non-Passkey methods)
  │
  └──WebAuthn──▶ go-webauthn RP (self-hosted)
                    │
                    ├─ Passkey registration (credential stored in DB)
                    ├─ Passkey authentication (assertion verification)
                    ├─ Credential public key available
                    └─ JWT issued by self-hosted RP
                           │
                           ▼
                    Go Backend (accepts JWT from BOTH issuers)
                      │
                      ├─ users.id → Safe address (UNCHANGED)
                      └─ Ticket / Entry handlers (UNCHANGED)
```

## Design Principles (Already in Place)

These principles are implemented in the MVP to ensure a smooth migration:

### 1. `users.id` as Universal Identifier

All ticket system tables (`tickets`, `merkle_tree`, `nullifiers`) use `users.id` (internal UUIDv7) as foreign key. Never `users.external_id` (Zitadel sub) or credential-specific values.

**Why this enables migration**: Safe address derivation (`CREATE2(salt = keccak256(users.id))`) is auth-provider-agnostic. Changing the auth mechanism does not affect on-chain identity or ticket data.

### 2. Configurable JWT Issuer List

The backend's JWT validation accepts a list of trusted issuers:

```yaml
auth:
  accepted_issuers:
    - "https://zitadel.example.com"       # Existing Zitadel issuer
    # - "https://passkey.example.com"      # Future go-webauthn issuer (Option C)
```

**Why this enables migration**: Adding a second issuer is a configuration change, not a code change. Both Zitadel JWT and self-hosted JWT are validated by the same `jwx` middleware.

### 3. User Linking via `external_id`

The `users` table has an `external_id` column that maps to the Zitadel `sub` claim. In Option C, a user authenticated via go-webauthn can be linked to the same `users.id` by matching on a shared identifier (e.g., email verified by both systems).

## Migration Steps

### Phase 1: Add go-webauthn RP (Parallel Operation)

1. **Add `go-webauthn/webauthn` v0.15.0** to the backend Go module
2. **Create `webauthn_credentials` table**:
   ```sql
   CREATE TABLE webauthn_credentials (
     id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id    UUID NOT NULL REFERENCES users(id),
     credential_id    BYTEA NOT NULL UNIQUE,
     public_key       BYTEA NOT NULL,
     sign_count       BIGINT NOT NULL DEFAULT 0,
     authenticator_aaguid BYTEA,
     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```
3. **Create `webauthn_sessions` table** for transient challenge state:
   ```sql
   CREATE TABLE webauthn_sessions (
     id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     challenge  BYTEA NOT NULL UNIQUE,
     user_id    UUID REFERENCES users(id),
     session_data JSONB NOT NULL,
     expires_at TIMESTAMPTZ NOT NULL,
     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```
4. **Implement Connect RPC handlers** for `PasskeyService`:
   - `BeginRegistration` → generate challenge, persist session
   - `FinishRegistration` → verify credential, store in `webauthn_credentials`
   - `BeginAuthentication` → look up credential, generate challenge
   - `FinishAuthentication` → verify assertion, issue JWT
5. **Issue JWT from self-hosted RP** with a distinct issuer URL
6. **Add self-hosted issuer** to `accepted_issuers` config list

### Phase 2: Frontend Integration

1. **Add `@simplewebauthn/browser`** to the frontend
2. **Implement Passkey registration/authentication UI** that calls the self-hosted RP endpoints
3. **Maintain `oidc-client-ts`** flow as fallback for non-Passkey users
4. **Route users** to appropriate auth flow based on capability detection

### Phase 3: Gradual Migration

1. **New Passkey registrations** go through self-hosted RP (credential stored locally)
2. **Existing Zitadel Passkeys** continue to work through Zitadel hosted UI
3. **Users can re-register** Passkeys with the self-hosted RP at their discretion
4. **No forced migration** — both paths coexist indefinitely

## What Does NOT Change

| Component | Reason |
|---|---|
| `users.id` (UUIDv7) | Universal identifier; all FKs reference this |
| `users.safe_address` | Derived from `users.id`; auth-agnostic |
| `tickets`, `merkle_tree`, `nullifiers` tables | Reference `users.id` only |
| Safe address derivation logic | `CREATE2(keccak256(users.id))`; no auth dependency |
| ZKP verification flow | Independent of auth mechanism |
| Ticket minting flow | Uses `users.id` → Safe address; no auth dependency |

## What Changes

| Component | Option A (MVP) | Option C (Migration) |
|---|---|---|
| WebAuthn RP | Zitadel | go-webauthn (self-hosted) |
| Credential storage | Zitadel internal | `webauthn_credentials` table |
| Login UI | Zitadel hosted | Custom (Aurelia 2) |
| JWT issuers | 1 (Zitadel) | 2 (Zitadel + self-hosted) |
| Frontend auth library | `oidc-client-ts` only | `oidc-client-ts` + `@simplewebauthn/browser` |
| Backend auth deps | `jwx` only | `jwx` + `go-webauthn/webauthn` |

## Estimated Effort

| Phase | Scope | Effort |
|---|---|---|
| Phase 1 (Backend) | go-webauthn integration, DB tables, RPC handlers, JWT issuance | 3-5 days |
| Phase 2 (Frontend) | @simplewebauthn integration, auth routing UI | 2-3 days |
| Phase 3 (Migration) | Testing, gradual rollout, documentation | 1-2 days |
| **Total** | | **6-10 days** |

## Monitoring Checklist

- [ ] Watch [Issue #8282](https://github.com/zitadel/zitadel/issues/8282) for resolution (RPOrigins bug)
- [ ] Watch [Discussion #8867](https://github.com/zitadel/zitadel/discussions/8867) for Conditional UI support
- [ ] Watch `go-webauthn/webauthn` [Discussion #218](https://github.com/go-webauthn/webauthn/discussions/218) for v1.0 API stability
- [ ] Review Zitadel release notes for credential public key export capability
