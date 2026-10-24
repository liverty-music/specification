## 1. Proto (specification)

- [ ] 1.1 Add to `rpc/admin/order/v1/order_service.proto`:
  - `OrderService.ListByEvent(ListByEventRequest { entity.v1.EventId event_id })` returning `repeated entity.v1.Order orders`, with protovalidate (`event_id` required) and a doc comment listing UNAUTHENTICATED, PERMISSION_DENIED and INVALID_ARGUMENT;
  - in the `Refund` comment, the FAILED_PRECONDITION for the reason CANCELLATION while the Order's Event is not CANCELLED (design D4, D9).

  Verify `make check`
- [ ] 1.2 In `rpc/admin/concert/v1/concert_service.proto`:
  - add optional `entity.v1.ArtistId artist_id = 1` to `ListRequest`;
  - document that List returns only that Artist's Concerts when it is set;
  - rewrite the `Delete` comment: it is refused while the Event has an Order that is not refunded, a settlement that is not reversed or a purchase in progress; it removes the Event with its refunded purchases, resale listings, scanner records and an emptied Organizer series; it suppresses the slot for discovery only (design D5, D9).

  Verify `make check` and `buf breaking` (additive)
- [ ] 1.3 Merge, publish a GitHub Release and confirm `buf-release.yml` succeeded

## 2. Event removal and its blockers (backend: entity operations)

- [ ] 2.1 Consume the released schema; verify `make check`
- [ ] 2.2 Implement the shared per-Event removal and the shared blocker predicate in `rdb` (design D1, D2). Rebuild `ConcertRepository.DeleteAndSuppress` on them as a transaction. Verify integration tests for components/entity/concert/delete-and-suppress:
  - "Concert with fan journeys", "Series stays", "Concert with an abandoned checkout";
  - "Cancelled concert with refunded purchases", "Last event of a first-party series", "Other events of a first-party series";
  - "Concert with issued tickets", "Concert with a held settlement", "Concert with a checkout in progress", "Concert with an open lottery entry";
  - "Unknown id", "Slot already suppressed".
- [ ] 2.3 Add the catalog-driven foreign-key test (design D3). It builds the full fixture, deletes the event, and fails when `pg_constraint` shows a table referencing an event's records that the fixture leaves empty. Verify it passes. Verify it fails when the `resale_listings` step of 2.2 is commented out.
- [ ] 2.4 Switch `OrganizerRepository.Delete` to the shared removal and blocker predicate. Verify integration tests for components/entity/organizer/delete:
  - "Organizer with a published Series", "Refunded purchase", "Resold ticket";
  - "Active Organizer", "Paid order", "Settlement", "Purchase in progress", "Payout account".

  Also verify the existing OrganizerUseCase.Delete unit tests still pass.
- [ ] 2.5 Add `ConcertRepository.List`'s optional artist filter. Verify integration tests for components/entity/concert/list: "Narrowed to one artist", "Artist without concerts", and the existing four scenarios.
- [ ] 2.6 Declare and implement `Order.ListByEvent` and `Order.GetEventID` on `entity.OrderRepository`. Verify integration tests for:
  - components/entity/order/list-by-event: "Paid, refunded and resale orders", "Orders of another event", "No event given";
  - components/entity/order/get-event-id: "Order from a checkout", "Order from a won lottery entry", "Unknown order".
- [ ] 2.7 Return the publish state from `Event.Get`. Verify integration tests for components/entity/event/get: "Cancelled event", "Discovered event", and the existing three scenarios.
- [ ] 2.8 Remove the suppression check from `checkSlot` and update the comments in `internal/entity/series.go` and `internal/usecase/series_uc.go` (design D6). Verify integration tests for:
  - components/entity/series/publish-events: "Suppressed slot", "Another Organizer's slot", "Cancelled slot";
  - components/entity/series/update: "Suppressed new slot", "First-party event at the new slot", "Start time announced", "Discovered event at the new slot".

## 3. Usecases and admin handlers (backend)

- [ ] 3.1 Add the CANCELLED-Event check to `OrderUseCase.Refund` for the reason Cancellation (design D4). Verify unit tests for components/usecase/order/refund:
  - "Cancellation refund for an event still on sale", "Cancellation refund for a cancelled event", "Dispute for an event still on sale";
  - "Reason missing", "Repeated refund", "Unknown order".
- [ ] 3.2 Add `OrderUseCase.ListByEvent`. Verify unit tests for components/usecase/order/list-by-event: "Cancelled event with refunded and paid orders", "Unknown event".
- [ ] 3.3 Pass the optional Artist through `ConcertUseCase.List`, and return the deletion's FailedPrecondition from `ConcertUseCase.Delete`. Verify unit tests for:
  - components/usecase/concert/list: "One artist's concerts", "Catalog and queue both populated", "Unlisted Organizer concert";
  - components/usecase/concert/delete: "Concert with issued tickets", "Cancelled concert after refunds", "Auto-published concert deleted", "Missing id", "Unknown id".
- [ ] 3.4 Verify unit tests for components/usecase/series/publish: "Suppressed slot", "Claims a discovered event".
- [ ] 3.5 Add `ListByEvent` to the admin order handler, and the `artist_id` mapping to the admin concert handler's List. Verify handler tests for:
  - components/adapter/admin/api/rpc/order: "Admin lists an event's orders", "Event missing", "Non-admin lists orders";
  - components/adapter/admin/api/rpc/concert: "Admin lists one artist's concerts", "Malformed artist id".
- [ ] 3.6 Merge and cut the backend Release. Confirm the prod rollout of `fan-api` and `admin-console-api` reached the new version.

## 4. Admin console (frontend)

- [ ] 4.1 Consume the released schema. Add `create` to the admin artist client, `listByEvent` to the admin order client, and the `artistId` argument to the admin concert client's `list`. Verify `make check`.
- [ ] 4.2 On the Organizers screen:
  - add `Create test artist` (name field, the hint, a generated v4 UUID, Create then AssociateArtist, retry of the association only);
  - make each roster Artist link to the Artist concerts screen (design D7).

  Verify component tests for components/infrastructure/admin/web/route/organizers: "Test artist created and associated", "Association fails after registration", "Empty name", "Open an artist's concerts".
- [ ] 4.3 Build the Artist concerts screen at `artists/:artistId/concerts`, with rows, `Refund all` and `Delete` (design D8). Verify component tests for components/infrastructure/admin/web/route/artist-concerts:
  - "Cancelled concert with paid orders", "No concerts";
  - "All refunded", "Refund stops part-way", "Published concert", "Dismissed";
  - "Refunded cancelled concert deleted", "Delete blocked by a paid order", "Delete dismissed".
- [ ] 4.4 Merge and cut the frontend Release. Confirm the admin console image rolled out in prod.

## 5. Switch the test Organizer to a test Artist (operations, prod)

Run after group 7 is released.

- [ ] 5.1 On the Organizers screen, create a test Artist for `e2e-test` with a name no real artist uses. Verify it is listed in the roster.
- [ ] 5.2 In the organizer console, cancel every Series of `e2e-test` that names the real Artist, which also removes its DRAFT Events. Verify the Artist concerts screen of the real Artist shows those Concerts as `Cancelled`.
- [ ] 5.3 On that screen, use `Refund all` for each cancelled Concert with Paid Orders, then `Delete` for every one. Then verify with a read-only prod query that:
  - the Organizer has no Event naming the real Artist;
  - no Order of those Events remains;
  - each deleted Event's page is not found.

  Mark components/infrastructure/admin/web/route/artist-concerts and stories/remove-a-cancelled-concert "Cancelled, refunded and deleted" verified here (`@spec-manual`, citing this task).
- [ ] 5.4 In the organizer console, try to publish a test DRAFT at the slot of a deleted Event. Verify it succeeds, which covers stories/delete-a-wrong-concert "Organizer publishes into the slot" (`@spec-manual`, citing this task). Then cancel that test Event.
- [ ] 5.5 Remove the real Artist from `e2e-test` with the roster's Remove, and unfollow it with the prod E2E fan. Verify the roster lists only the test Artist.
- [ ] 5.6 Recreate the prod E2E Events for the test Artist (public, unlisted, cancelled, upcoming, sale and resale fixtures as the specs in `frontend/e2e/prod` need). Run `npm run test:e2e:prod` with the new ids. Verify every spec passes.
- [ ] 5.7 Write `frontend/docs/prod-e2e-fixtures.md`, linked from the header of `frontend/playwright.prod.config.mjs`. It covers:
  - which spec needs which Event;
  - how to create the Events for the test Artist;
  - how to obtain `E2E_ORGANIZER_TOKEN`;
  - how to retire used Events with Cancel, `Refund all` and `Delete`.

  Verify that the document is merged.
- [ ] 5.8 Cover the remaining story scenarios:
  - stories/remove-a-cancelled-concert "Refund before cancellation" and "Delete before refunds", through the unit tests of 3.1 and 3.3 and the screen tests of 4.3 (`@spec` on the screen tests);
  - stories/delete-a-wrong-concert "Discovery finds it again", through the existing concert-creation unit test.

  Verify `scripts/check-scenario-coverage.py` passes for this change.

## 6. Follow-up issues

- [ ] 6.1 File issues for:
  - releasing open lottery entries and held checkouts when an Event is cancelled;
  - notifying fans of a refund;
  - the payout-account contradiction in components/entity/organizer/delete.

  Verify the three issue links are recorded here.

## 7. Review fixes (proto, backend, frontend)

- [ ] 7.1 In `rpc/admin/concert/v1/concert_service.proto` add `ListByArtist(ListByArtistRequest { entity.v1.ArtistId artist_id })` (required) returning concerts, series and artists like `List`; remove `ListRequest.artist_id` and reserve field 1 and its name; update the `Delete` comment to the D2 blockers. In `rpc/admin/artist/v1/artist_service.proto` add `Get(GetRequest { entity.v1.ArtistId artist_id })` returning `entity.v1.Artist artist`. Each with protovalidate and the doc comment's error list (D9, D10). Verify `make check`; open the PR with the `buf skip breaking` label.
- [ ] 7.2 Merge, publish a GitHub Release and confirm `buf-release.yml` succeeded.
- [ ] 7.3 Consume the release. In `rdb`, lock the events, their ticket types and those ticket types' checkouts and lottery entries `FOR UPDATE` before the blocker check in both deletions; block on a Paid Order and on a Draft lottery entry with a card authorization; remove Failed orders with the Refunded ones and only Completed, Expired and Released checkouts (D1, D2). Verify integration tests for:
  - components/entity/concert/delete-and-suppress: "Cancelled concert with a failed order", "Concert with a draft entry holding a card authorization", and the existing scenarios;
  - components/entity/organizer/delete: "Draft entry with a card authorization", and the existing scenarios;
  - a test that starts a checkout on the Event in a second transaction while a deletion holds its locks, and verifies the checkout is refused and nothing it created is removed.
- [ ] 7.4 Restore `ConcertRepository.List` and `ConcertUseCase.List` to take no Artist; add `Concert.ListCatalogByArtist` and `ConcertUseCase.ListCatalogByArtist`, and `ArtistUseCase.Get`. Verify:
  - integration tests for components/entity/concert/list-catalog-by-artist: "Narrowed to one artist", "Artist without concerts", "Draft event excluded", "No artist given";
  - unit tests, with the mockery mocks, for components/usecase/concert/list-catalog-by-artist: "One artist's concerts", "Missing artist"; components/usecase/artist/get: "Known artist", "Unknown artist"; and the existing components/usecase/concert/list and delete scenarios (replacing the `fakeConcertRepo` filter and `deleteErr` added in 3.3).
- [ ] 7.5 Add the admin handlers `ConcertService.ListByArtist` and `ArtistService.Get`, and drop the `artist_id` mapping from `List`. Verify handler tests for components/adapter/admin/api/rpc/concert: "Admin lists one artist's concerts", "Malformed artist id", "Missing artist id", "Non-admin lists an artist's concerts"; components/adapter/admin/api/rpc/artist: "Admin reads an artist", "Missing ArtistId", "Unknown artist", "Non-admin reads an artist".
- [ ] 7.6 Merge and cut the backend Release. Confirm the prod rollout of `fan-api` and `admin-console-api` reached the new version.
- [ ] 7.7 Consume the release in the frontend. The Artist concerts screen reads the Artist with `ArtistService.Get` and lists with `ConcertService.ListByArtist`; the roster link carries the id only; remove `?name=`, the name taken from the Concerts and the id fallback. Update the refused-Delete copy of both screens. Share the local-date formatting with the approved-concerts screen and replace the test double's `outcome` hook with a plain mock. Verify component tests for components/infrastructure/admin/web/route/artist-concerts: "No concerts", "Unknown artist", "Delete blocked by a paid order", and the existing scenarios; components/infrastructure/admin/web/route/organizers: "Open an artist's concerts", "Delete blocked by an order"; and `make check`.
- [ ] 7.8 Merge and cut the frontend Release right after 7.6. Confirm the admin console rolled out in prod. Then, signed in as an admin, run the Organizers → Artist concerts flow with Playwright against prod, read-only: open an Organizer's roster link, check the heading names the Artist, and open and dismiss both dialogs without confirming.

