## Context

The sibling change `fix-push-notification-toggle-sync` introduces `PushNotificationService` RPCs that carry an explicit `user_id` in the request, verified against the JWT-derived userID in the handler, with mismatches rejected as `PERMISSION_DENIED`. The rationale is defense-in-depth: if a client bug constructs a request for the wrong user, the backend catches it rather than silently operating on the JWT-inferred user.

`UserService` today follows a different pattern: the client sends no user identifier, and the backend resolves everything from the JWT. Adopting two inconsistent patterns in the same codebase is a long-term liability — every future reviewer has to relearn which service does which thing, and every future service author has to make the same decision again without obvious precedent.

This change aligns `UserService` to the new convention so the authenticated RPC surface is uniform. The exception is `UserService.Create`: at call time, the internal user record does not yet exist, so there is no `user_id` the caller could send that could be verified against anything — `external_id` (Zitadel `sub`) remains the only meaningful identity for that RPC.

## Goals / Non-Goals

**Goals:**
- Establish a single, documented convention: every authenticated per-user RPC body carries an explicit `user_id` verified against the JWT.
- Migrate `UserService.Get`, `UpdateHome`, and `ResendEmailVerification` to follow the convention.
- Extract the JWT-match check into a shared helper so it is implemented once and reused across services.
- Document `Create`-style RPCs as the one sanctioned exception to the convention.

**Non-Goals:**
- Services that have no per-user semantics (e.g., `ConcertService.List`, `ArtistService.Search`) are out of scope — they do not carry a user identifier because they are not scoped to a user.
- Revising the JWT validation / `authn-go` middleware stack. That layer remains as defined in the `authentication` capability.
- Introducing role-based access control or admin RPCs.

## Decisions

### D1: `Create` is the sanctioned exception, and is documented as such

**Decision:** `UserService.Create` does not gain a `user_id` field. The convention is stated as "every authenticated RPC body carries an explicit `user_id` **once the caller's internal user ID exists**".

**Rationale:** A caller cannot send an internal `user_id` before that ID has been minted. The RPC derives the internal ID from `external_id` (Zitadel `sub`) during the create path, and the resulting `user_id` is returned to the caller for use on subsequent RPCs. Forcing a fake field here would degrade the convention's clarity.

**Alternatives considered:**
- *Have the client pre-generate the UUID and send it.* Would preserve symmetry but introduces client/server coupling on UUID format and collision semantics. The generation timing is better owned by the backend.
- *Replace `Create` with `CreateOrGet` returning the existing record on re-invocation.* Out of scope; the current create semantics work.

### D2: Shared helper / interceptor for the JWT-match check

**Decision:** Implement the check as a helper function invoked at the start of each relevant handler. The helper takes the caller's already-resolved internal user ID alongside the request-supplied value (rather than reading the JWT userID from `ctx`), because every per-user handler already needs to resolve the caller via `GetByExternalID(ctx, externalID)` to perform its real work — passing that resolved ID into the helper avoids a duplicated resolution step inside the helper itself:

```go
// internal/adapter/rpc/mapper/user.go
func RequireUserIDMatch(callerUserID, reqUserID string) error {
    if reqUserID == "" {
        return connect.NewError(connect.CodeInvalidArgument, errors.New("user_id is required"))
    }
    if reqUserID != callerUserID {
        return connect.NewError(connect.CodePermissionDenied, errors.New("user_id does not match authenticated user"))
    }
    return nil
}
```

Handler call site pattern:

```go
externalID, err := mapper.GetExternalUserID(ctx)
if err != nil { return nil, err }
user, err := h.userUseCase.GetByExternalID(ctx, externalID)
if err != nil { return nil, err }
if err := mapper.RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue()); err != nil {
    return nil, err
}
// ... business logic ...
```

**Rationale:** A Connect interceptor is attractive but would need per-RPC configuration to know which field holds the `user_id` (since proto messages have no uniform field name at that layer). A helper function keeps each handler explicit about what it is checking, while still being a one-liner at the top of each RPC. Simplicity wins over the pseudo-magic of an interceptor.

The `(callerUserID, reqUserID)` signature was chosen over `(ctx, reqUserID)` because the handler must resolve the caller's internal UUID anyway (`external_id` in the JWT vs. `user_id` UUID in the database are distinct identities); making the helper consume the already-resolved value keeps the resolution path explicit and avoids hiding a DB call inside what looks like a pure validation helper.

**Alternatives considered:**
- *Connect interceptor with per-message reflection.* Rejected: fragile reflection, no benefit when a one-line helper does the same job.
- *Generated code via a protoc plugin.* Over-engineered for the current footprint; revisit only if the service count grows past ~10.
- *`(ctx, reqUserID)` signature with the helper resolving the caller internally.* Rejected for the reason above — would either duplicate the `GetByExternalID` lookup or force the helper to take a repository dependency.

### D3: Ordering behind `fix-push-notification-toggle-sync`

**Decision:** This change's PR lands after `fix-push-notification-toggle-sync` is merged.

**Rationale:** The push notification fix is urgent (user-visible bug). This standardization has no user-visible urgency. Keeping them in separate PRs also reduces review surface. Both changes introduce `requireMatchingUserID`; the first one to land owns the helper's creation, and the second consumes it.

**Alternatives considered:**
- *Merge into a single change.* Rejected per the user's guidance — 2-change split was chosen deliberately.

### D4: Frontend userID source and persistent cache

**Decision:** The frontend persists the authenticated userID to `localStorage` keyed by `external_id` (Zitadel `sub`), and `UserServiceClient` reads/writes this cache transparently. `UserService.current` remains the in-memory runtime handle; the localStorage layer is the across-reload source of truth.

**Rationale:** Prior to this change, the userID was only ever in memory — populated by the first `Get` response. With `Get` now requiring a `user_id`, the "first Get learns our own userID" pattern breaks. A small localStorage cache fills the gap: the first time a userID is learned (from `Create` or a prior `Get`), it is persisted; on subsequent boots the cache is read **before** any RPC is issued.

**Cache shape:**
- Key: `liverty:userId:<external_id>` (where `<external_id>` is `auth.user.profile.sub`)
- Value: the UUID string of the internal `user_id`
- Writer: `UserServiceClient` on every successful `Get` / `Create` / `UpdateHome` response
- Reader: `UserServiceClient` on-demand, keyed by the current OIDC `sub`
- Clear: `UserServiceClient.clear()` removes the entry for the current `sub` on sign-out

**Cache-miss recovery (see D5):** when the cache is empty — fresh device, cleared storage, or post-sign-up — the frontend calls `UserService.Create` unconditionally. `Create` is the sanctioned exception (D1) and now also behaves idempotently (D5), so it always returns the user entity whether the record is new or pre-existing. The returned userID is then written to the cache for all subsequent calls.

### D5: `UserService.Create` becomes idempotent on duplicate `external_id`

**Decision:** Change `UserService.Create`'s behavior so that a duplicate `external_id` returns the existing user (HTTP success, `CreateResponse.user` populated) instead of `connect.CodeAlreadyExists`.

**Rationale:** The returning-user boot path needs a way to learn its own `user_id` without already having one. `Create` is the only RPC in the exempted bootstrap surface (D1). Making it idempotent gives the frontend a single, uniform way to resolve userID from `external_id` on any device: "call Create; the response always carries my userID." This removes the old two-step `Get` → `NotFound` → `Create` → `AlreadyExists` → `Get` dance entirely.

**Semantic note:** The change is backward-compatible for the sign-up path (new user) — the response shape is unchanged. It IS a semantic change for the sign-in-on-new-device path: instead of `ALREADY_EXISTS`, the caller sees success. The frontend update removes the `ALREADY_EXISTS` branch.

**Alternatives considered:**
- *Dedicated `GetSelf` boot RPC (no `user_id`, returns `{ user_id, user }`).* Rejected: adds a second bootstrap RPC when one already exists, and weakens the "only `Create` is exempt" story.
- *Include the existing user in the `ALREADY_EXISTS` error detail.* Rejected: abuses error payloads to carry success data; Connect's error-detail pattern is not idiomatic for this.
- *Leave `Create` as-is and return `ALREADY_EXISTS` + store userID server-side keyed by external_id in a cookie.* Rejected: cookie adds cross-cutting state; localStorage cache keyed by `sub` is simpler client-side.

## Risks / Trade-offs

- **Risk:** Frontend boot flow breaks if the userID is not available before the first `UserService.Get`. → **Resolved by D4 + D5**: a localStorage cache keyed by `external_id` feeds the userID to boot-time `Get`; an idempotent `Create` provides a uniform cache-miss recovery path that always yields a userID.
- **Risk:** Breaking the request shape causes clients on older bundles to hit `INVALID_ARGUMENT` (missing `user_id`) after the backend deploys. → Mitigation: standard frontend-follows-backend deploy order; old bundles are transient.
- **Trade-off:** Every call site is slightly more verbose. → Mitigation: the `PushService`/`UserService` frontend wrappers abstract the `user_id` injection so business code still calls `userService.get()` without passing it explicitly.
- **Trade-off:** The JWT check duplicates work already done by the `authn-go` middleware. → Mitigation: defense-in-depth is the whole point. The middleware authenticates; the handler authorizes the specific user scope.

## Migration Plan

1. Merge specification PR; publish Release; BSR gen completes.
2. Merge backend PR. Handlers now require `user_id` in the request and reject missing or mismatched values.
3. Merge frontend PR. All call sites inject the cached userID.
4. Old frontend bundles in the wild will start receiving `INVALID_ARGUMENT` on the three RPCs; users refreshing will pick up the new bundle and recover. No server-side migration needed.

**Rollback:** Revert in reverse (frontend → backend → specification). Because proto types change, a partial rollback fails — revert as a set.

## Open Questions

- ~~On frontend boot, is the userID reliably available before the first `UserService.Get`?~~ **Resolved:** audit confirmed the userID is NOT reliably available on boot (no persistent cache exists today; returning users rely on the first `Get` response to learn their own userID). Addressed by D4 (localStorage cache keyed by `external_id`) and D5 (idempotent `Create` for cache-miss recovery).
- ~~Should the helper live in a shared package reused by `PushNotificationService` (introduced by `fix-push-notification-toggle-sync`)?~~ **Resolved:** both consumers (`UserService` and `PushNotificationService`) already live in the same flat `internal/adapter/rpc/` package, so the helper is implemented as a package-private function in a new file (e.g., `auth.go`) alongside the handlers. No new subpackage is created; YAGNI wins. If a future service lives outside that package and needs the same check, promote it then.
