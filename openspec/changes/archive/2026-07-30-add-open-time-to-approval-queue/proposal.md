## Why

The concert approval queue table shows start time but omits open time (door-open time), even though the backend already captures `OpenTime` on `StagedConcert`. Reviewers cannot see this field, and the conflict dialog's staged side hardcodes `—` for open time. Exposing it makes the queue consistent with the approved-concerts page and gives reviewers complete timing context when judging a staged concert.

## What Changes

- Add `open_time` field to the `PendingConcert` proto message so open time is carried over the wire
- Map `StagedConcert.OpenTime` in the backend `PendingConcertToProto` mapper
- Add an **Open time** column to the approval queue table in the admin frontend, positioned after Start time
- Fix the conflict dialog's staged side to display the actual staged open time instead of a hardcoded `—`

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `concert-approval-queue`: The approval queue SHALL display open time alongside start time in the reviewer table; the `PendingConcert` RPC message SHALL carry the `open_time` field

## Impact

- **specification**: `proto/liverty_music/rpc/admin/v1/concert_service.proto` — `PendingConcert` message
- **backend**: `internal/adapter/rpc/mapper/pending_concert.go` — `PendingConcertToProto`; `internal/adapter/rpc/mapper/concert_test.go`
- **frontend**: `admin/approval-queue/approval-queue-route.ts` (`QueueRow`, `ConflictView`, `toRow`, `toConflictView`); `admin/approval-queue/approval-queue-route.html`
- No DB migration required (data already stored on `staged_concerts.open_at`)
- No breaking change — adding an optional field to `PendingConcert` is wire-compatible
