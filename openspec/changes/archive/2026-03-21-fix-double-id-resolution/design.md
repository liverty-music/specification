## Context

The codebase has two distinct patterns for ID resolution (external Zitadel sub → internal UUID):

**Pattern A — UseCase-layer resolution** (pre-PR #246 pattern, used by `FollowUseCase`):
```
Handler receives claims.Sub → passes to UseCase → UseCase calls GetByExternalID internally
```

**Pattern B — Handler-layer resolution** (introduced in PR #246 for TicketJourney, TicketEmail):
```
Handler calls GetByExternalID → passes user.ID to UseCase → UseCase uses it directly
```

PR #246 incorrectly applied Pattern B to `FollowHandler` even though `FollowUseCase` already implements Pattern A via `resolveUserID()`. This caused double resolution: the handler passed `user.ID` (UUID) to `uc.ListFollowed`, which then called `GetByExternalID(user.ID)` — querying the `external_id` column with a UUID that was never stored there → `not_found`.

## Goals / Non-Goals

**Goals:**
- Fix `FollowService/ListFollowed`, `Follow`, `Unfollow`, `SetHype` returning `not_found`
- Establish a clear rule: each use case uses exactly one pattern — never both

**Non-Goals:**
- Unifying all use cases to a single pattern (that is a larger refactor)
- Changing `TicketJourneyUseCase` or `TicketEmailUseCase` (they correctly use Pattern B)

## Decisions

**Decision: Revert `FollowHandler` to pass `claims.Sub` directly to the use case.**

`FollowUseCase.resolveUserID()` already owns ID resolution for all follow operations. The handler should not duplicate this. Pattern B (handler-layer resolution) is only appropriate when the use case has no internal resolution.

Alternatives considered:
- Remove `resolveUserID` from `FollowUseCase` and keep handler-layer resolution → would require touching the use case and all its tests; higher blast radius; Pattern B is less clean for use cases with multiple methods all needing resolution.
- Add a rule to `resolveUserID` to detect UUID input and skip → fragile, no clear ownership.

**Decision: `FollowHandler` does not hold a `userRepo` reference.**

Since the handler no longer calls `GetByExternalID`, the `userRepo` dependency is not needed. Removing it makes the handler's dependency surface smaller and its tests simpler.

## Risks / Trade-offs

- [Risk] Other use cases may have the same double-resolution bug → Mitigation: audit `TicketJourneyUseCase` and `TicketEmailUseCase` to confirm they do NOT call `resolveUserID` internally (they don't — handler-layer resolution is the sole path for those).

## Migration Plan

1. Revert `follow_handler.go`: remove `userRepo`, pass `claims.Sub` to use case
2. Update `di/provider.go`: remove `userRepo` from `NewFollowHandler`
3. Update `follow_handler_test.go`: remove `MockUserRepository`, pass `claims.Sub` as userID in mock expectations
4. Deploy — no DB migration needed
