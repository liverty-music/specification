## 1. Proto Schema Changes (specification repo)

- [x] 1.1 Move `EventId` message from `ticket.proto` to `event.proto`
- [x] 1.2 Update `ticket.proto` to import `EventId` from `event.proto` (remove local definition)
- [x] 1.3 Replace `ConcertId` with `EventId` in `Concert.id` field (concert.proto line 15)
- [x] 1.4 Delete `ConcertId` message from `concert.proto` (lines 49-53)
- [x] 1.5 Add `import "liverty_music/entity/v1/event.proto"` to `concert.proto`
- [x] 1.6 Run `buf lint` and `buf format -w` to validate schema
- [x] 1.7 Verify `buf breaking` flags expected changes (will use `buf skip breaking` label on PR)

## 2. Backend Changes (backend repo)

- [x] 2.1 Update RPC mapper `ConcertToProto` to use `entityv1.EventId` instead of `entityv1.ConcertId`
- [x] 2.2 Remove any remaining references to `ConcertId` in mapper or handler code
- [x] 2.3 Run `go build ./...` to verify compilation after BSR gen publishes new types
- [x] 2.4 Run backend tests to verify no regressions

## 3. Frontend Changes (frontend repo)

- [x] 3.1 Search for `ConcertId` references in TypeScript code and replace with `EventId`
  - No `ConcertId` proto type references found; `concert.id?.value` still works as field name unchanged
- [x] 3.2 Run `make lint` and `make test` to verify no regressions
  - No code changes required; no frontend PR needed

## 4. Release Coordination

- [x] 4.1 Create specification PR with `buf skip breaking` label
- [x] 4.2 Merge specification PR and create GitHub Release (triggers BSR gen)
- [x] 4.3 Create backend PR
- [x] 4.4 Create frontend PR (draft until BSR gen completes)
  - Not needed — no frontend code references `ConcertId` type
