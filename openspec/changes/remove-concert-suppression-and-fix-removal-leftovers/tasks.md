Section 0 is a specification proto PR with doc comments only; it needs no release, since generated code does not change behaviour. Each backend section below is one PR that passes `make check` on its own. Sections 0 to 4 may merge in any order; section 5 merges after section 1 has been released to prod; section 6 is the close-out.

## 0. specification: proto doc comments

- [ ] 0.1 Rewrite the doc comments that describe suppression: `admin/concert/v1/concert_service.proto` Delete (the slot is no longer suppressed; an unknown id changes nothing) and `organizer/series/v1/series_service.proto` Update (drop "a suppressed slot" from the FAILED_PRECONDITION causes) and Publish (drop the sentence about a slot an admin suppressed). Verify with `buf lint`, `buf format` and buf breaking passing, and `git grep -i suppress -- proto` returning nothing

## 1. backend: one Event delete, no suppression in code (components/entity/concert/delete, entity/order, entity/series, usecase/concert/delete, usecase/concert/create-from-discovered)

- [ ] 1.1 Add `OrderStatus.LeavesWithEvent()` and `Series.LeavesWithLastEvent()` (design.md D1). Verify with entity table tests for every scenario of "An Order leaves with its Event only when ended" (Void, Refunded, Paid, Pending) and "A first-party series leaves with its last event" (first-party left empty, discovered left empty, series with events left)
- [ ] 1.2 In `event_removal.go`, build the removable Order statuses from `LeavesWithEvent()` and remove emptied Series by reading them under the removal's locks, filtering with `LeavesWithLastEvent()` and deleting `WHERE id = ANY($ids) AND NOT EXISTS (events)`. Verify with the existing catalog-driven removal test and the Concert.Delete and Organizer.Delete integration tests passing unchanged
- [ ] 1.3 Remove the lock-free `ConcertRepository.Delete` and its tests, rename `DeleteAndSuppress` to `Delete` across entity, rdb, usecase and mocks, and drop its suppression insert. Verify with rdb integration tests annotated `@spec components/entity/concert/delete` for every scenario of that spec, including "Same slot created again after the delete" (Concert.Create at the deleted slot makes a new Event) and the existing purchase-blocker scenarios; closes backend#700
- [ ] 1.4 Remove `SuppressedConcert` (entity, `SuppressedConcertRepository`, rdb repository and tests, mock), the `Exists` gate, its tally and the `suppressed_count` property of the ingest signal in `ConcertCreationUseCase.CreateFromDiscovered`, and the DI wiring in `internal/di/worker.go`; keep the `suppressed_concerts` table. Verify with a `CreateFromDiscovered` unit test that an event at a slot where a Concert was deleted is published, the ingest signal tests of "Each batch reports what it did" without a suppressed count, `go build ./...`, and `git grep -i suppress -- internal` returning only the rejected-concert comment
- [ ] 1.5 Update `ConcertUseCase.Delete` and its tests to the scenarios of `usecase/concert/delete` ("Concert deleted", "Missing id", "Unknown id", "Concert with issued tickets", "Cancelled concert after refunds"). Verify with `concert_uc_admin_test.go` annotated per scenario

## 2. backend: TicketStock delete keeps Orders it did not check (backend#741, components/entity/ticket-stock/delete)

- [ ] 2.1 Write by hand a migration that replaces `delete_ticket_stock` with each DELETE filtered to Void Orders (design.md D4). Functions stay out of `schema.sql` (backend AGENTS.md, schema section; `db-migration-workflow` skill), so no `atlas migrate diff` for this one; update the migration directory's checksum with `atlas migrate hash`. Verify with CI's Atlas CI job and the integration tests of 2.2 and 2.3
- [ ] 2.2 Add an integration test that, in two connections, inserts a lottery entry's Pending Order for the stock while `delete_ticket_stock` runs, in both interleavings (insert committed before the delete, and insert started after the delete's lock), and asserts the invariant: either the delete fails with FailedPrecondition and the Order survives, or the insert is refused and no Order that is not Void was removed. Record in design.md D4 which outcome each interleaving produced. Verify with the test passing under `make test`
- [ ] 2.3 Add a table test over every `entity.OrderStatus` value: only a stock whose Orders are all Void is deleted. Verify with the test annotated `@spec components/entity/ticket-stock/delete` for "Stock with a pending order" and "Stock with a paid order"; closes backend#741

## 3. backend: rate limiter clock (backend#739)

- [ ] 3.1 Give `ratelimit.Limiter` an injected `now func() time.Time` (production `time.Now`), use `AllowN(now(), 1)`, and rewrite `TestInterceptor` with a fake clock. Verify with `go test -count=50 ./internal/infrastructure/server/ratelimit/` passing; closes backend#739

## 4. backend: admin handlers and the natural-key race (backend#701, backend#310)

- [ ] 4.1 Remove the hand-written required-field checks and `connect.NewError` calls from `admin_notification_handler.go` and `admin_order_handler.go` where the proto field is annotated required; move any other check into the usecase as an `apperr` InvalidArgument; keep the production-only refusal in the notification handler, returned as an `apperr` PermissionDenied; and make `OrderUseCase.Refund` take the time from its injected `Clock` instead of the handler's `time.Now()` and the Stripe webhook's receive time (design.md D5). Verify with the handler tests through the admin interceptor pipeline returning the same codes as before (annotated with the scenarios of `adapter/admin/api/rpc/notification`, including "Production"), and a usecase test that Refund reads the fake clock, with the handler tests annotated for `adapter/admin/api/rpc/order` "Refund passes the reason" and the webhook tests of `adapter/fan/api/webhook/payment-events` "A dispute refunds the Order" passing; closes backend#701
- [ ] 4.2 Re-read `ConcertRepository.Create` against backend#310. If two concurrent creates of one natural key can still both report a new id, add a failing integration test and fix it; otherwise close backend#310 with the evidence (code lines and why the race cannot happen). Verify with the test, or with the issue's closing comment

## 5. backend: drop the suppression table (after section 1 runs in prod)

- [ ] 5.1 Read-only in prod (cloud-provisioning runbook, ephemeral db-proxy Pod): record the count of `suppressed_concerts` rows and how many slots match a Venue and date of a published Event, in design.md D3. Verify by the recorded numbers
- [ ] 5.2 Add a migration that drops `suppressed_concerts` (schema.sql, then `atlas migrate diff`). Verify with `make lint-schema`, CI's Atlas CI job, and the prod AtlasMigration status `Applied` after the merge

## 6. Close-out (specification)

- [ ] 6.1 At archive, edit the Purpose of `components/usecase/concert/delete` (no suppression) and the Purpose and sequence diagram of `components/usecase/concert/create-from-discovered` (no SuppressedConcert participant, three outcomes), and delete the emptied specs `components/entity/concert/delete-and-suppress`, `components/entity/suppressed-concert`, `components/entity/suppressed-concert/exists` and `stories/delete-a-wrong-concert`. Verify with `openspec validate --specs` and `python3 scripts/check-spec-layout.py`
