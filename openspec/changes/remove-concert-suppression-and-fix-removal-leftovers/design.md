## Context

See proposal.md (Why). The admin delete reaches `ConcertUseCase.Delete` → `ConcertRepository.DeleteAndSuppress` (backend `internal/infrastructure/database/rdb/concert_repo.go`). That method takes the removal locks and asks `entity.EventRemovalBlockers.Check()` through `lockAndCheckEventRemoval`, removes the records through `removeEvents` (`event_removal.go`, shared with `OrganizerRepository.Delete`), and inserts a `suppressed_concerts` row in the same transaction. Discovery reads that table through `SuppressedConcertRepository.Exists` in `ConcertCreationUseCase.CreateFromDiscovered` (`concert_creation_uc.go`). Two decisions of the removal are still written in rdb: the Order statuses that leave with an Event (`endedOrders`, Void and Refunded) and the Series that leave with their last Event (`removeEmptiedFirstPartySeriesQuery`, `organizer_id IS NOT NULL`).

Usecases have no transaction of their own (no unit of work in `internal/usecase`); every write that must be atomic across tables is one repository operation.

## Goals / Non-Goals

**Goals:**
- Remove suppression end to end: code, table, specs.
- One delete path for an Event, with its locks and checks; no lock-free `Delete`.
- The removal's per-record decisions are entity predicates; rdb applies them under its locks.
- Close backend#741, #739, #701 and #310 without changing what callers see, except #741's fix.

**Non-Goals:**
- A usecase-level transaction (unit of work). Moving the composition of a removal into the usecase needs one, and that decision touches every multi-table write (48 transactions in rdb today). It is a separate change if wanted.
- Restricting which Concerts an admin can delete. The console reaches Delete only from Artists an Organizer represents, and the blockers protect every live purchase.

## Decisions

### D1 — Concert.Delete keeps the composition; entities own the per-record rules

- `ConcertRepository.DeleteAndSuppress` is renamed `Delete`; the old lock-free `Delete` (`DELETE FROM events`, no caller outside tests) and its tests go.
- The composition (which records go with an Event) stays in the one repository operation, because it must run inside the transaction that holds the removal locks: a check made outside it would miss a purchase started after the check. Its list is stated in the spec `components/entity/concert/delete`.
- New entity predicates, named after the spec requirements:
  - `OrderStatus.LeavesWithEvent() bool`: Void or Refunded.
  - `Series.LeavesWithLastEvent() bool`: true for a first-party Series (an Organizer is set).
- rdb applies them as compare-and-set:
  - The Order statuses passed to the delete statements are built from `OrderStatus` values for which `LeavesWithEvent()` is true, not from a hand-written list.
  - The emptied Series are read (id and organizer) under the removal's locks, mapped to `entity.Series`, filtered with `LeavesWithLastEvent()`, and deleted with `WHERE id = ANY($ids) AND NOT EXISTS (events of the series)`.
- Rejected: the usecase composing `Delete` calls of each repository. Without a transaction in the usecase the steps are not atomic and the check runs outside the locks.

### D2 — Locks of Concert.Delete are unchanged

The rows locked are the ones `eventRemovalLockQueries` lock today (TicketStocks, then their Checkouts, LotteryEntries, ResaleEntries and Orders, then the Events), and every purchase path reaches a stock through its row lock or a foreign-key check (FOR KEY SHARE), so a purchase started after the check waits and then fails on the removed rows. Removing suppression and moving the predicates do not change this order.

### D3 — Suppression is removed in two deploys

- First, the code stops reading and writing `suppressed_concerts`: `SuppressedConcert` entity and repository, the `Exists` gate and its tally in `CreateFromDiscovered`, the insert in `Delete`, DI wiring and mocks.
- Then a migration drops `suppressed_concerts`. Splitting keeps running pods of the previous release (which still read the table) working while the new release rolls out; the AtlasMigration can run before the new pods are ready.

### D4 — delete_ticket_stock keeps its decision in SQL (backend#741)

- `delete_ticket_stock` is `SECURITY DEFINER` so that `organizer-console-api` holds EXECUTE on one function instead of DELETE on `orders`, `checkouts`, `lottery_entries`, `resale_entries` and `card_authorizations`. Passing the removable statuses in from Go would let that role remove Orders of any status, so the Void-only rule stays inside the function: this is the one place where the decision does not move to an entity, by design.
- Each DELETE in the function is filtered by `status = 5` (Void), the state its check allowed, as `removeEvents` already does: an Order that is not Void is left in place and its RESTRICT foreign key fails the whole delete.
- Locks: the function locks the stock row `FOR UPDATE`. An Order insert takes `FOR KEY SHARE` on the same row through its foreign key, so an insert after the lock waits and then fails, and an insert before it is committed before the check runs. The race in backend#741 is therefore probably already prevented; that is inferred from PostgreSQL's row-lock conflicts, not observed. A test that runs a lottery-entry insert concurrently with the delete verifies it, and the filters are a second guard either way.
- A table test over every `entity.OrderStatus` value checks that only Void Orders let the delete through, so a new status cannot silently become removable.

### D5 — Leftovers

- backend#739: `ratelimit.Limiter` takes `now func() time.Time` (as `NewClientThrottle` does) and calls `rate.Limiter.AllowN(now(), 1)`; the test advances a fake clock instead of depending on wall-clock timing.
- backend#701: the admin notification and order handlers drop their hand-written required-field checks and `connect.NewError` calls; protovalidate and the apperr interceptor give the same codes. Where a field is not annotated as required in the proto, the check stays and moves into the usecase as an `apperr` InvalidArgument (no proto change in this change). The production-only PermissionDenied of the debug RPC stays a usecase or interceptor decision, not a handler `connect.NewError`.
- backend#310: re-read `ConcertRepository.Create` against the current upsert; if two concurrent creates of one natural key can still both report a new id, fix it with an integration test; otherwise close the issue with the evidence.

## Risks / Trade-offs

- [A real concert at a slot of a deleted test Event was skipped by discovery in the past] → After this change discovery no longer skips it; the next search finds it. Nothing restores a past skip.
- [Dropping `suppressed_concerts` loses its rows] → They only ever guarded test data; the read-only prod check before the drop records their count and slots.
- [D4 keeps a business rule in SQL] → Accepted for least privilege; the status table test ties it to the entity's status set.

## Migration Plan

1. Release the code without suppression (D3 first step) and the `delete_ticket_stock` replacement migration.
2. After that release is running in prod, record the count of `suppressed_concerts` rows read-only, then merge the migration that drops the table.
Rollback: step 1 is a code rollback; step 2 cannot restore rows, which only guarded test data.
