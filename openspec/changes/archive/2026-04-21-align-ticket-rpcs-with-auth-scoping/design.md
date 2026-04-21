## Context

The `standardize-user-scoped-rpc-auth` change (archived 2026-04-20) elevated the `rpc-auth-scoping` capability into `openspec/specs/`. Its core requirement — every authenticated per-user RPC SHALL carry an explicit `entity.v1.UserId` that the backend verifies against the JWT-derived userID — is now a cross-service convention. `UserService.Get`, `UserService.UpdateHome`, `UserService.ResendEmailVerification`, and `PushNotificationService` already comply.

The ticket system's RPC surface was designed earlier under a different philosophy:

```proto
// Current (ticket_service.proto)
message MintTicketRequest {
  liverty_music.entity.v1.EventId event_id = 1 [(buf.validate.field).required = true];
  reserved 2;           // deliberately not user_id
  reserved "user_id";
}
message ListTicketsRequest {
  reserved 1;
  reserved "user_id";
}

// Current (entry_service.proto)
message GetMerklePathRequest {
  liverty_music.entity.v1.EventId event_id = 1 [(buf.validate.field).required = true];
  reserved 2;
  reserved "user_id";
}
```

Handler code follows the JWT-only pattern:

```go
// Current ticket_handler.go (simplified)
externalID, _ := mapper.GetExternalUserID(ctx)
user, _ := h.userRepo.GetByExternalID(ctx, externalID)
// proceed with user.ID — no request field to verify against
```

The `implement-ticket-system-mvp` change is at 72/79 tasks (remaining are manual verifications). Its spec deltas for `ticket-management` and `zkp-entry` have not yet been promoted to `openspec/specs/`. This change is the last clean seam to align the RPC surface before the capability specs ship in their current form.

## Goals / Non-Goals

**Goals:**
- Bring `MintTicket`, `ListTickets`, `GetMerklePath` onto the `rpc-auth-scoping` convention (explicit `user_id` + JWT-match check).
- Keep the change atomic and small — a single proto PR, a single backend PR, a single frontend PR.
- Reuse the existing `mapper.RequireUserIDMatch` helper. Do not introduce new abstractions.
- Ship before `implement-ticket-system-mvp` is archived so the capability specs enter `specs/` already compliant.

**Non-Goals:**
- Changing `GetTicket`. It is keyed by `ticket_id` (not user-scoped at the request boundary); the existing uniqueness of a ticket ID is sufficient authorization scoping. Adding `user_id` would be ceremony without a threat model.
- Changing `VerifyEntry`. Explicitly unauthenticated — the ZK proof itself is the authentication. The scanner device is operator-controlled; there is no "JWT" to match against.
- Changing any repository, use-case, or entity-layer code. The ownership check lives entirely in the adapter layer.
- Touching the `tickets`, `merkle_tree`, or `nullifiers` schemas.
- Retrofitting `GetTicket` into a user-scoped RPC (future work if threat modeling calls for it).
- Updating manual-verification.md in the MVP change (that change's owner updates it when the new proto fields land).

## Decisions

### Decision 1: Add `user_id` to the three breaking requests, not to `GetTicketRequest`

Alternatives considered:
- **A. Add `user_id` to all five RPCs including `GetTicket` and `VerifyEntry`.** Rejected. `VerifyEntry` is unauthenticated so there is no JWT to match; adding `user_id` would create a field with no enforcer. `GetTicket` is identifier-scoped — the canonical example in Google AIP of a resource read-by-name, not a user-scoped operation.
- **B. Only change the two user-listing RPCs (`ListTickets`, `GetMerklePath`) and leave `MintTicket` JWT-only.** Rejected. `MintTicket` writes a record keyed to a user; the `rpc-auth-scoping` spec explicitly states the convention applies to every authenticated per-user RPC except creation RPCs that mint an internal user ID. `MintTicket` does not mint a user ID — it mints a ticket for an existing user — so it falls under the convention.
- **C. Chosen — surgical: three breaking requests (`MintTicketRequest`, `ListTicketsRequest`, `GetMerklePathRequest`).** These are exactly the requests where the authenticated caller acts on their own user-scoped data.

### Decision 2: Reuse the `user_id` field number `2` that was previously reserved

Alternatives considered:
- **A. Use a fresh field number (3 or higher).** Rejected. Proto3 field-number reuse rules only prohibit reusing a number whose tag was *in use* at any wire-compatible version. `reserved 2` on these messages was never assigned in a released proto — the field was reserved from the start. Taking field 2 keeps the wire layout tidy.
- **B. Chosen — reuse field 2 for `user_id`.** Matches the pattern already used by `UserService.GetRequest` / `UpdateHomeRequest` / `ResendEmailVerificationRequest` (all of which placed `user_id` at field 2). Consistent with the rest of the authenticated RPC surface.

For `ListTicketsRequest`, `user_id` takes field 1 (it is the only field). This matches `ListFollowsRequest` and other user-listing patterns.

### Decision 3: Delegate the match check to `mapper.RequireUserIDMatch` — no new helper

Alternatives considered:
- **A. Introduce a ticket-specific interceptor that automatically enforces the match.** Rejected. The ticket handler already has its own reason to call `userRepo.GetByExternalID` (to resolve Safe address for `MintTicket`). Adding an interceptor layer duplicates the lookup.
- **B. Chosen — call `mapper.RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue())` inline in each handler**, mirroring `UserHandler.Get` / `UpdateHome` / `ResendEmailVerification`. Single precedent, single pattern.

### Decision 4: Breaking-change discipline — one release, no shim window

Alternatives considered:
- **A. Two-phase: make `user_id` optional first, accept absence for one release, then make it required.** Rejected. No external consumers today besides this monorepo. A shim window buys nothing and costs review time.
- **B. Chosen — single BREAKING release**, coordinated with backend + frontend PRs per the standard cross-repo release workflow. `buf skip breaking` label on the spec PR.

### Decision 5: Frontend `user_id` source = existing `localStorage` cache

The `standardize-user-scoped-rpc-auth` change already introduced the `externalId → userId` cache in `localStorage`, read via `UserServiceClient` on every RPC dispatch. Ticket RPC call sites plug into the same code path; no new cache, no new key.

## Risks / Trade-offs

- **Risk: BSR gen delay blocks backend/frontend PRs.** → Mitigation: follow the workspace's standard cross-repo release protocol — prepare backend/frontend branches locally against the planned type shape (placeholder `any`-typed `user_id` today, swap to generated types after BSR gen). Do not open the downstream PRs as drafts before BSR gen completes.
- **Risk: A ticket RPC call site in the frontend misses the cached `user_id`, causing `INVALID_ARGUMENT` from protovalidate in production.** → Mitigation: exhaustive grep-based audit of `ticketService.*` and `entryService.*` call sites; pair with TypeScript strict checks on the generated request types after BSR gen (missing required field becomes a compile error).
- **Risk: Manual verification runbook in `implement-ticket-system-mvp/manual-verification.md` has `curl` snippets that omit `user_id`.** → Mitigation: not in scope for this change. Flagged in tasks.md as a follow-up for the MVP change owner when they pick up 10.x/11.x/14.x.
- **Trade-off: The `MintTicket` handler still has to call `userRepo.GetByExternalID` first** (to know `user.ID` for the match), before calling `RequireUserIDMatch`. The check is therefore not "free" as it would be under a generic interceptor. Accepted — the `GetByExternalID` call is already required for the Safe-address lookup that happens on first mint, so no new database work is introduced.
- **Trade-off: `GetTicket` remains identifier-scoped and therefore follows a different authorization pattern** than the other ticket RPCs. Accepted — documented explicitly in the spec delta and the design above. If threat modeling later justifies tightening `GetTicket`, it will be a separate change.

## Migration Plan

Standard cross-repo release coordination:

1. **specification**: branch, commit proto + spec delta changes, open PR with `buf skip breaking` label. CI validates lint/format. Wait for review.
2. **Parallelize**: backend + frontend branches created against the planned type shape (placeholder types; not pushed as PRs yet).
3. **Merge specification PR** once reviewed.
4. **Publish GitHub Release** on specification (tag `vX.Y.Z`, marked as containing breaking changes) → triggers `buf-release.yml` → BSR publishes.
5. **Monitor BSR gen** until success.
6. **Upgrade dependency**: `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.Z` in backend; `npm install @buf/liverty-music_schema.connectrpc_es@latest` in frontend.
7. **Swap placeholders**: replace placeholder types with generated types at the call sites; run `make check` in each repo.
8. **Open backend and frontend PRs** only after local `make check` passes in both. CI should pass on first push.

**Rollback**: If an incident shows up post-deploy, revert the spec repo PR, publish a reversion release. Because no database or user-data change is involved, rollback is purely a wire-format revert; no migration is required.

## Open Questions

(None. The design re-uses all existing helpers, existing cache infrastructure, and the established cross-repo release workflow.)
