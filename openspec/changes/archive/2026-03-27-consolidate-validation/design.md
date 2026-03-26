## Context

The backend has three layers of input validation:

1. **Protovalidate interceptor** (`connectrpc.com/validate`) — validates all request messages against `buf.validate` annotations before handlers execute. Already registered as the innermost interceptor.
2. **Handler (adapter) layer** — ~35 manual checks (nil guards, empty string, enum map lookups) that duplicate protovalidate rules.
3. **Usecase layer** — ~49 parameter guards, of which ~30 duplicate proto validation, ~11 check JWT-derived `userID`, and ~8 are domain invariants.

Additionally, handlers inconsistently pass either external IDs (`claims.Sub`) or internal UUIDs to usecases, leaking IdP concerns into the domain layer.

## Goals / Non-Goals

**Goals:**
- Establish a single validation boundary: protovalidate interceptor for proto-derived fields, handler helper for JWT-derived identity.
- Usecases trust all inputs unconditionally — zero validation guards.
- All usecases receive internal user UUID, never external ID.
- Reduce handler boilerplate to: extract identity → map proto to domain → delegate to usecase.

**Non-Goals:**
- Changing proto `buf.validate` annotations (already comprehensive).
- Modifying entity-layer domain invariants (`Home.Validate()`, Ethereum address regex, ZKP verification).
- Changing the interceptor chain ordering or adding new interceptors.
- Refactoring the mapper package beyond the new helper function.

## Decisions

### D1: Remove all handler input validation

**Decision:** Delete every manual nil/empty/enum check in handler files.

**Rationale:** The protovalidate interceptor runs before handlers and enforces identical constraints via `buf.validate` annotations. These checks are unreachable dead code. Audit confirmed all 35 handler checks have corresponding proto annotations.

**Alternative considered:** Keep checks as defense-in-depth.
**Rejected because:** Double validation creates maintenance drift risk — when a proto annotation changes, the handler check silently diverges. The interceptor is the authoritative boundary.

### D2: Remove all usecase input validation

**Decision:** Delete every `InvalidArgument` guard in usecase files, including `userID == ""` checks.

**Rationale:** If the policy is "usecases trust inputs", there should be no exceptions. Selective checking (e.g., only `userID`) is worse than no checking because it implies a contract that other parameters are validated elsewhere while `userID` is not — which is misleading once the handler guarantees it.

**Where validation remains:**
- `entity.Home.Validate()` — cross-field domain invariant (country-level1 prefix). Called by `user_uc.UpdateHome` and `user_uc.Create`.
- `entity.ParseZKPPublicSignals()` / `signals.VerifyEventID()` — cryptographic verification, not input validation.
- `ticket_uc.validateMintParams` Ethereum address regex — domain constraint not expressible in proto. **This stays but moves to entity layer** as `entity.ValidateEthereumAddress(addr string) error`.

**Alternative considered:** Keep usecase guards for JWT-derived values only.
**Rejected because:** Inconsistent policy. Handler already guarantees non-empty `userID` via `GetExternalUserID` + `GetByExternalID` (which returns `NotFound` for unknown users).

### D3: Introduce `GetExternalUserID(ctx)` helper

**Decision:** Add a single function in `mapper/user.go`:

```go
func GetExternalUserID(ctx context.Context) (string, error) {
    claims, ok := auth.GetClaims(ctx)
    if !ok || claims == nil {
        return "", connect.NewError(connect.CodeUnauthenticated,
            errors.New("authentication required"))
    }
    if claims.Sub == "" {
        return "", connect.NewError(connect.CodeUnauthenticated,
            errors.New("token missing subject claim"))
    }
    return claims.Sub, nil
}
```

**Rationale:** Consolidates claims extraction + empty-sub guard into one call. Returns `Unauthenticated` (not `InvalidArgument`) because an empty `Sub` is a token integrity issue. Existing `GetClaimsFromContext` remains available for handlers that need full claims (e.g., `Create` which uses `Email` and `Name`).

### D4: Unify handler identity pattern to internal UUID

**Decision:** All handlers resolve `claims.Sub` → internal `User.ID` before calling usecases.

Current state:
- **Pattern A** (follow, concert): pass `claims.Sub` (external ID) directly to usecase.
- **Pattern B** (ticket, ticket_journey, ticket_email, push_notification): resolve to internal UUID first.

After change: all use Pattern B.

**Rationale:** The domain layer should not know about IdP identifiers. `claims.Sub` is a transport concern. Internal UUID is the domain identity.

**Affected usecases and repositories:**
- `follow_uc.Follow(userID, artistID)` — `userID` changes from external ID to internal UUID.
- `follow_uc.Unfollow(userID, artistID)` — same.
- `follow_uc.SetHype(userID, artistID, hype)` — same.
- `follow_uc.ListFollowed(userID)` — same.
- `concert_uc.ListByFollower(externalUserID)` — parameter becomes internal UUID.
- `concert_uc.ListByFollowerGrouped(externalUserID)` — same.
- Follow and concert repositories update queries from `external_id` to `user_id` (internal UUID).

**Migration note:** The follow DB table currently stores `external_user_id`. This column will be migrated to `user_id` referencing the `users` table. Concert queries that join through follow → user will also be updated.

### D5: Simplify enum mapping in handlers

**Decision:** Remove `ok` guard from enum map lookups. After interceptor guarantees `defined_only`, the map lookup always succeeds for valid proto enum values.

```go
// Before
status, ok := mapper.TicketJourneyStatusFromProto[req.Msg.Status]
if !ok {
    return nil, connect.NewError(connect.CodeInvalidArgument, ...)
}

// After
status := mapper.TicketJourneyStatusFromProto[req.Msg.Status]
```

**Risk:** If a new proto enum value is added but the Go mapper map is not updated, the lookup returns zero-value silently.
**Mitigation:** Mapper tests already cover all enum values. CI catches missing mappings.

### D6: Move Ethereum address validation to entity layer

**Decision:** Extract `ethAddressRe` regex from `ticket_uc.validateMintParams` to `entity.ValidateEthereumAddress(addr string) error`.

**Rationale:** This is a domain invariant (what constitutes a valid Ethereum address), not input validation. It belongs alongside `Home.Validate()` in the entity layer. The usecase calls it as a business rule check, not as parameter guard.

## Risks / Trade-offs

**[Risk] Usecase called from non-handler context with bad inputs**
→ Currently all usecases are only called from handlers. If a future CLI or batch job calls usecases directly, it bypasses protovalidate. Mitigation: document in usecase package godoc that callers must provide validated inputs. This is the standard Clean Architecture contract — usecases define the interface, callers satisfy preconditions.

**[Risk] Follow DB migration (external_id → user_id)**
→ Requires Atlas migration to rename/replace column and backfill data. Mitigation: migration runs via Atlas operator before new code deploys (sync wave ordering). Backfill joins `users.external_id` to resolve internal UUIDs.

**[Risk] Enum zero-value after mapper lookup (D5)**
→ If mapper map is incomplete, handler passes zero-value to usecase silently. Mitigation: existing mapper unit tests enumerate all proto enum values. Add a compile-time exhaustiveness check if Go supports it (or generator-based approach).

**[Trade-off] More DB lookups in follow/concert handlers**
→ Resolving `claims.Sub` → `User.ID` adds one `GetByExternalID` call per request where there was none before. These handlers previously avoided the lookup. Impact: one indexed query per request (~1ms). Acceptable for architectural consistency.
