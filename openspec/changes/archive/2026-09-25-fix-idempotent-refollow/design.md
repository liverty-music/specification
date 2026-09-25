## Context

`FollowRepository.Follow` (`internal/infrastructure/database/rdb/follow_repo.go`) executes `followInsertQuery`, which uses `ON CONFLICT DO NOTHING`. pgx reports no error for a no-op conflict, so a duplicate insert and a fresh insert are indistinguishable to the caller today. `FollowUseCase.Follow` already has an `errors.Is(err, apperr.ErrAlreadyExists)` branch that treats it as success (see proposal.md - Why), and the entity interface's doc comment already declares `AlreadyExists` as a possible error of `Follow`; only the repository implementation is out of step.

## Goals / Non-Goals

**Goals:**
- Make `FollowRepository.Follow` distinguish "row inserted" from "row already existed" and report the latter as `apperr.ErrAlreadyExists`, matching the already-declared entity contract.

**Non-Goals:**
- Changing the RPC-facing behavior of `Follow` (it must keep succeeding for the caller on a repeat follow — that is `FollowUseCase.Follow`'s job, already implemented).
- Changing `ON CONFLICT DO NOTHING` to an UPSERT — the row and its hype level must stay untouched on a duplicate, which `DO NOTHING` already guarantees; only the RowsAffected reporting changes.

## Decisions

### Use `pgx.CommandTag.RowsAffected()` rather than a pre-check SELECT

**Choice**: Keep the single `INSERT ... ON CONFLICT DO NOTHING` statement, but inspect the `pgconn.CommandTag` it returns. When `RowsAffected() == 0`, return `apperr.New(codes.AlreadyExists, "already following")` instead of `nil`. This mirrors the existing pattern in `FollowRepository.SetHype`, which already checks `tag.RowsAffected() == 0` and returns `apperr.New(codes.NotFound, ...)`.

**Alternatives considered**:
- A `SELECT ... FOR UPDATE` existence check before the insert: adds a round trip and a race window (TOCTOU) that `ON CONFLICT` avoids entirely.
- Removing `ON CONFLICT DO NOTHING` and mapping the raw unique-violation (`23505`) through `toAppErr`: `toAppErr` already maps `23505` to `AlreadyExists`, but this would make Postgres raise-and-catch a constraint error on every repeat follow, which is noisier (and slower under load) than reading the command tag of a no-op insert. Also indistinguishable from `SetHype`'s tag-based style used elsewhere in this file.

## Risks / Trade-offs

- [Risk] Any other caller of `FollowRepository.Follow` that assumed "never errors on duplicate" would now see `AlreadyExists`. → Mitigation: `FollowUseCase.Follow` is the only caller (grep-confirmed) and already handles it as the success path; no other caller exists to break.
