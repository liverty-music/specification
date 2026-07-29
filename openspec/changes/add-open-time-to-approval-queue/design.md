## Context

The `StagedConcert` domain entity already stores `OpenTime *time.Time`. When a concert is
discovered, the pipeline may capture the door-open time and persist it to `staged_concerts.open_at`.
However, the `PendingConcert` proto message (`rpc/admin/v1/concert_service.proto`) has no
`open_time` field, so the backend mapper drops the value and the frontend never receives it.

The approved-concerts page already renders `openTime` for published events via the `Concert` entity.
The conflict dialog's "Existing" side already shows `existingOpenTime` (from `ExistingEvent`), but
the "Staged" side hardcodes `—` because `PendingConcert` carries no open time.

This is a purely additive change with no DB migration, no behavioral logic change, and no
breaking proto change (optional field addition is wire-compatible under proto3).

## Goals / Non-Goals

**Goals:**
- Expose `open_time` in `PendingConcert` so reviewers can see it in the queue table
- Fix the conflict dialog's staged side to show the actual staged open time
- Keep the change minimal and fully additive

**Non-Goals:**
- Changing how open time is discovered or stored (already works)
- Altering approval/rejection logic
- Adding open time to the rejection log display

## Decisions

### Decision: Add `open_time` as field 10 on `PendingConcert`

`open_time` is optional (absent when the source did not state a door-open time). Field numbers
1–9 are already assigned; field 10 is the next available slot. Using the existing `entity.v1.OpenTime`
wrapper type is consistent with how `StartTime` is modelled (`entity.v1.StartTime`). No
`buf.validate` required constraint since this is genuinely optional data.

Alternatives considered:
- Embedding the timestamp directly as `google.protobuf.Timestamp` — rejected for inconsistency
  with the rest of the entity fields, which all use typed wrapper messages.

### Decision: Map in `PendingConcertToProto`, not in the handler

`pending_concert.go` is the dedicated mapper for `PendingConcert`; the handler should not
know mapping details. This is consistent with how `StartTime` is already mapped there (line 31–33).

### Decision: Frontend adds `openTime` to `QueueRow` and `toConflictView`

`QueueRow` precomputes all display strings so the template stays free of optional-chaining.
Adding `openTime: string` follows the same pattern as `startTime`. The conflict view gets
`stagedOpenTime` to replace the hardcoded `—` on the staged side.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| spec → BSR gen → backend/frontend pipeline adds latency | Backend and frontend can be implemented in parallel with the spec PR; only the package upgrade step gates the final push |
| `open_at` may be NULL for most staged rows | `formatTimeOfDay` already returns `—` for absent timestamps; no special handling needed |
| `ConflictView.stagedOpenTime` is a pre-formatted string (set in `toRow()` at page-load time) while `existingOpenTime` is formatted lazily from the raw proto `Timestamp` at conflict-display time — if `formatTimeOfDay`'s locale behavior changes in the future, both sides of the dialog will not update simultaneously | Accepted trade-off: the asymmetry mirrors the existing pattern where all `QueueRow` display strings are precomputed. A future change to `formatTimeOfDay` will require a page reload to apply on the staged side. |
