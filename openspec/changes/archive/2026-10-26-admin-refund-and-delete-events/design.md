## Context

See proposal.md for the motivation. The approach is shaped by these facts in the current code:

- **Two deletion paths, written separately:**
  - `ConcertRepository.DeleteAndSuppress` (backend `internal/infrastructure/database/rdb/concert_repo.go`) is one CTE statement. It deletes the event, its moneyless checkouts and its emptied ticket sales, and inserts the suppression row. A Ticket, Order or Settlement makes the statement fail.
  - `OrganizerRepository.Delete` (`organizer_repo.go`, around line 471) runs its own ordered DELETEs in one transaction, with a dry-run blocker check that the usecase calls first.
  - Neither handles `resale_listings` (migration `20261020081056_create_resale_listings.sql`, added after both). A resale listing references the ticket, the checkout and the ticket type with `ON DELETE RESTRICT`.
- **Foreign keys under an event:**
  - RESTRICT: `tickets.event_id`, `settlements.event_id`, `scanners`, `admissions`, `rejected_scans`; and via ticket types, `checkouts`, `resale_listings`.
  - RESTRICT between purchase records: `orders` from `checkouts` and `lottery_entries`; `tickets` and `settlements` from `orders`.
  - CASCADE: `ticket_types` (then `lottery_entries`), `concerts`, `concert_artists`, `ticket_journeys`, `settlement_splits`, `referrals`.
- **Refund:**
  - `OrderUseCase.Refund` (`order_refund_uc.go`) has two callers: the admin handler, and the Stripe webhook with the reason Dispute only.
  - `Order.CommitRefund` voids the Order's Tickets, cancels its Listed resale listings and reverses its Settlement in one transaction.
- **Suppression in the Series path:** `checkSlot` in `series_events_repo.go` (around line 217) checks it for both `PublishEvents` and the start-time change in `Update`. Discovery checks it separately, in the concert-creation consumer, through `SuppressedConcert.Exists`.
- **Admin console:**
  - It already mounts the fan `ArtistService` on the admin server (`internal/di/provider.go`, around line 624), so `ArtistService.Create` is reachable with the admin token.
  - Routes live in `frontend/admin/admin-shell/admin-shell.ts`. The Organizers screen holds the roster, the artist search and Associate.
- **Production:** the Stripe key is a test-mode key (`cloud-provisioning/src/index.ts`, around line 50). Refunds of the test Events move no real money. The dev environment is stopped, so verification is unit and integration tests plus the prod operation in tasks.md.

## Goals / Non-Goals

**Goals:**
- One definition of "remove an Event and what depends only on it", used by Concert deletion and by Organizer deletion.
- A test that fails when a new table references an event's records but the removal does not handle it.
- A cancellation refund that cannot run for an Event still on sale.

**Non-Goals:**
- Releasing card authorizations or open lottery entries when an Event is cancelled. Deletion refuses while they exist; the release itself is a follow-up issue.
- Telling fans about a refund.
- Removing payout accounts or Stripe objects.
- A server-side bulk refund. `Refund all` is a client loop over `OrderService.Refund`.
- An un-suppress operation.

## Decisions

### D1 — One per-Event removal, shared by both deletions

- A package-level function in `rdb` takes a transaction and a set of event ids. It removes, in this order:
  1. `admissions`, `rejected_scans`, `scanners`;
  2. `resale_listings` of the events' ticket types;
  3. the Reversed `settlements`;
  4. the `tickets` of the Refunded and Failed orders;
  5. the Refunded and Failed `orders`;
  6. the Completed, Expired and Released `checkouts` of the events' ticket types;
  7. the `events`. The cascade removes `ticket_types`, `lottery_entries`, `concerts`, `concert_artists` and `ticket_journeys`.
  8. the Organizer TicketSales left without a TicketType;
  9. the first-party `series` left with no event.
- **Locking.** Before the blocker check, the transaction locks, `FOR UPDATE` and child rows first: the `checkouts` and `lottery_entries` of the events' ticket types, then those `ticket_types`, then the `events`.
  - This is the order the purchase paths take. Creating a checkout or a Draft, moving one forward (Held to Committed, Draft to Entered) and issuing an Order (`IssuanceRepository.Issue`) all lock or update the checkout or lottery entry row first, and reach the ticket type or event only through a foreign-key check (`FOR KEY SHARE`) when they insert. Locking parents first would invert that order and let a removal and an issuance deadlock.
  - A path that inserts a new checkout, lottery entry, resale listing or ticket after the child rows are locked holds `FOR KEY SHARE` on its ticket type or event, so the removal waits for it at the parent lock and its blocker check, a new statement, then sees the new row. A path that starts after the parent locks waits, and then fails on the removed ticket type or event.
  - So a purchase started during the removal is either seen by the check or refused, never removed. The status filters in steps 4 to 6 are a second guard: a row in a state the check did not allow makes a RESTRICT foreign key fail the whole removal.
- `ConcertRepository.DeleteAndSuppress` becomes a transaction:
  1. Take the locks above.
  2. Read the event's slot; return with no effect when it is gone or DRAFT (Concert operations treat a DRAFT id as unknown).
  3. Run the blocker check (D2).
  4. Run the shared removal.
  5. Insert the suppression row.

  The method keeps its name and interface.
- `OrganizerRepository.Delete` keeps its lock, status check and dry run, and takes the same row locks over all its events before the check. It replaces its own event-level DELETEs with the shared removal over all its events, then deletes the remaining series, the series images and the organizer.
- **Rejected: changing the RESTRICT keys to CASCADE.** That is a migration, and a plain `DELETE FROM events` anywhere else would then silently remove purchases. The admin-delete-test-data design rejected it for the same reason.

### D2 — One blocker predicate

- One SQL fragment, parameterised by the event-id set, reports any of:
  - an `orders` row for the events' ticket types with status Paid. A Failed order's payment was already refunded (`OrderStatusFailed`), so it does not block and is removed with the Refunded ones;
  - a `settlements` row for the events with status not Reversed;
  - a purchase in progress:
    - a `checkouts` row that is Held or Committed;
    - an Expired or Released `checkouts` row with `card_authorization_id` set and `card_authorization_release_at` NULL;
    - a `lottery_entries` row that is Entered;
    - a Won `lottery_entries` row with no `orders` row: its payment is captured and the issuance sweeper has not yet issued its Order (`issuance_repo.go` `issuanceListAwaitingQuery`). The cascade would otherwise drop it and leave the captured payment with no Order to refund;
    - a Draft `lottery_entries` row with `card_authorization_id` set: the lottery path opens the card authorization while the entry is still Draft (`lottery_entry_repo.go`, the authorization update `WHERE state = 5`), and the cascade would otherwise drop it with the authorization open.
- The Concert path runs it inside its transaction. The Organizer path uses it both in the dry run and inside the transaction.
- It replaces Organizer.Delete's old "captured checkout not Completed" clause, which a Committed checkout already covers.

### D3 — A catalog-driven foreign-key test

- The integration test for D1 builds one event with a row in every table that holds a key to the event's records: event, ticket type, checkout, lottery entry, order, ticket, settlement and splits, resale listing, scanner, admission, rejected scan, journey and referral.
- It then deletes the event. A second assertion reads `pg_constraint` for every foreign key that references those tables and fails when a referencing table has no row in the fixture.
- So a future table with a RESTRICT key fails this test instead of failing a prod deletion after the external effects. That is how `resale_listings` was missed.
- The Organizer.Delete integration test reuses the fixture.

### D4 — The refund checks the Event through the Order

- `Order.GetEventID` lives on `entity.OrderRepository`. Its query joins the order's `checkout_id` or `lottery_entry_id` to the ticket type's `event_id`, the same join as Order.ListByEvent.
- `Event.Get` gains the publish state. The event read port's query adds `publish_state`, which is NULL for a discovered event.
- In `OrderUseCase.Refund`, after the already-Refunded early return and before any money moves:
  - for the reason Cancellation, call GetEventID, then Event.Get;
  - return FailedPrecondition unless the state is CANCELLED.

  The Dispute path is untouched, so the webhook is unaffected.
- **Rejected: a new admin `OrderService.RefundByEvent`.** The per-order `Refund` is already idempotent. The console loops over it, so a stopped run resumes by running it again.

### D5 — Listing for the console

- **New admin `ConcertService.ListByArtist(artist_id)`**, a separate RPC from `List`.
  - `rpc-design` (`.claude/skills/rpc-design/SKILL.md`, the `ListBy<Key>` row and "Key is an entity"): narrowing by an entity is a `ListBy<Key>` method with a required field; an optional field on `List` is for a state or a period.
  - It runs the new `ConcertUseCase.ListCatalogByArtist` and `Concert.ListCatalogByArtist`. The fan `Concert.ListByArtist` leaves out what fans cannot see, so the admin read is a separate operation, not a flag on it.
  - `List` and `Concert.List` stay as they were; the approved-concerts screen keeps calling `List`.
  - **Rejected: an optional `artist_id` on `ListRequest`**, shipped in v0.96.0. It made one method answer two questions, and `""` stood for "no artist" in Go. The field is removed and its number reserved (D9).
- **New admin `OrderService.ListByEvent(event_id)`** returns `repeated entity.v1.Order`.
  - `OrderRepository.ListByEvent` orders by `pay_at`.
  - The console sums the Paid ones per row. The test Artist has a handful of Concerts, so one call per first-party row is acceptable.

### D6 — Suppression leaves the Series path

- Remove the suppression query and its branch from `checkSlot`. It keeps the other-Organizer and CANCELLED-slot checks.
- Update the comments that list "suppressed" as a refusal in `internal/entity/series.go` and `internal/usecase/series_uc.go`.
- Discovery's `SuppressedConcert.Exists` check is unchanged, so the story `delete-a-wrong-concert` still holds for discovery.

### D7 — Test Artist creation in the console

- The form generates the MBID with `crypto.randomUUID()`, which gives a v4 UUID. It calls `ArtistService.Create` on the admin transport, then `OrganizerService.AssociateArtist`. The admin `artist-client` gains `create`.
- **Why nothing else changes for a fictional artist:**
  - `ArtistUseCase.Create` treats MusicBrainz's 404 as a failed lookup and keeps the given name. It announces nothing, so the name-resolution consumer never runs for it.
  - fanart.tv returns 404 once a week (an empty result).
  - The official-site refresh records "no URL" for an unknown MBID.
  - Gemini discovery skips the Artist while an active Organizer represents it.
  - Last.fm's `getsimilar` by MBID returns NotFound.
- The registered artist id is kept in the screen state until Associate succeeds, so a retry associates the same Artist.
- **Rejected: a nullable MBID, or an `is_test` flag on artists.** A nullable MBID makes the official-site refresh fail daily, and makes ListSimilar fall back to a name search that can persist real artists. A flag touches the schema, the jobs and the API, for protection the represented-artist exclusion already gives.

### D8 — The Artist concerts screen

- **Route:** `artists/:artistId/concerts` under the admin shell. It is linked from each roster row on the Organizers screen with the Artist's id only, and has a back link to Organizers.
- **Name:** read with admin `ArtistService.Get` (D10).
- **Rows:**
  - The state comes from the Concert's publish state; no publish state means `Discovered`.
  - Paid count and total come from `OrderService.ListByEvent` for first-party rows.
- **Refund all:** refund sequentially, update a progress count, stop at the first error, and re-read the Orders after each call.
- **Dialogs** follow the Organizers screen's Delete dialog: a modal `<dialog>`, initial focus on Cancel, and the destructive control disabled while the call is in flight.

### D9 — Proto comments

- `ConcertService.Delete` (admin) says today that it is unconditional and "NOT blocked by dependent rows". It is rewritten to state the blockers and what is removed.
- `OrderService.Refund` gains the CANCELLED-Event precondition for the reason Cancellation.
- These and the two new fields and method are one additive specification release (v0.96.0).
- A second release adds admin `ConcertService.ListByArtist` and admin `ArtistService.Get`, removes `ListRequest.artist_id` and reserves its number (`buf skip breaking`), and updates the `Delete` comment to the D2 blockers.

### D10 — The Artist concerts screen reads the Artist

- New admin `ArtistService.Get(artist_id)` returns one Artist, through a new `ArtistUseCase.Get` over the existing `Artist.Get`.
- The screen calls it with the route's id, so its heading is right for a deep link, a reload, and an Artist with no Concert.
- **Rejected: carrying the name from the Organizers screen in the URL (`?name=`)**, shipped in v1.120.0. The URL then decides what the screen shows, and the name is wrong for an edited or stale link. Reading the name from the Concerts response also fails for an Artist with no Concert.

## Risks / Trade-offs

- **[Risk] Deleting an Event removes its Order history.** → Mitigations:
  - Only Refunded Orders are removed.
  - Stripe keeps the payment and refund records.
  - The admin confirms each deletion.
  - The same trade-off was accepted in admin-delete-test-data.
- **[Risk] A `Refund all` run stops part-way (network, closed tab).** → `Refund` is idempotent, and the screen re-reads the Orders. Running it again refunds only the Orders still Paid.
- **[Risk] A held checkout or open lottery entry on a cancelled Event blocks deletion indefinitely.**
  - A Held checkout clears when its 15-minute hold expires and the sweeper releases it.
  - An Entered lottery entry clears only through the draw or withdrawal. That is the follow-up issue in the proposal; until then the admin can still refund, and deletion waits.
- **[Trade-off] The BREAKING refund precondition.** An admin can no longer issue a cancellation refund for an Event still on sale. No such refund is known to exist.
- **[Trade-off] The suppression row stays for a deleted Organizer Event.** It no longer affects the Organizer, and it keeps discovery from re-adding the slot, which is harmless.

- **[Risk] An admin console older than the second release calls `List` with `artist_id`.** The server ignores the unknown field and returns the whole catalog, with Delete on every row. → The backend and frontend releases go out back to back, the screen is not used in between, and only the owner holds the admin role.

## Migration Plan

1. **specification:** the proto change (admin `OrderService.ListByEvent`, admin `ConcertService.ListRequest.artist_id`, comments), then a PR, a Release and BSR generation.
2. **backend**, in one PR:
   - the shared removal and blocker predicate, with the catalog-driven FK test;
   - Order.ListByEvent, Order.GetEventID and Event.Get's publish state;
   - the refund precondition;
   - Concert.List's artist filter, which step 4 replaced with `ListByArtist` (D5);
   - suppression removed from the Series path;
   - the admin handlers.
   
   Then the release and its prod rollout.
3. **frontend:** the admin console Organizers additions and the Artist concerts screen, then the release.
4. **Review fixes** (tasks.md group 7), before the operations: the second specification release (D9), then the backend release with the locking and blocker changes (D1, D2), `ListByArtist` and `ArtistService.Get`, then the frontend release that reads the Artist and lists by Artist. The two application releases go out back to back.
5. **Operations (prod)** follow tasks.md group 5. Rollback is a revert of the backend release. Deletions already performed are not reversible, which is why each one is confirmed.

## Manual verification

@spec-manual stories/remove-a-cancelled-concert "Cancelled, refunded and deleted" -- Verified in prod on 2026-10-25 and 2026-10-26, observing each step on the e2e-test Organizer's `E2E Sale` Event of the test Artist, the only Event of its Series. Its 4 Paid Orders (15,000 yen, 5 Issued Tickets) were all one fan's, since the purchase spec's last-ticket race went to the same fan, not two.
- A member cancelled the Series in the organizer console.
- An admin used `Refund all` on the Artist concerts screen. A read-only prod query then found all 4 Orders Refunded, all 5 Tickets Voided and all 4 Settlements Reversed.
- The admin used `Delete`. The query then found no Event, no Series and no TicketType of the Event, and one suppression row for its slot.
- The fan API's ConcertService.Get for the Event returned `not_found`, and its page `/events/<id>` showed the not-found view.

Before this, tasks.md 5.2–5.3 had removed the nine BRADIO Series the same way on 2026-10-24, with 13 cancellation refunds, but recorded no Event ids to observe.

@spec-manual stories/delete-a-wrong-concert "Organizer publishes into the slot" -- Verified in prod by tasks.md 5.4 on 2026-10-24: in the organizer console, the e2e-test Organizer's member created a draft of the test Artist at the slot of a deleted Event (2026-12-01, Zepp Haneda, no start time), published it and saw the date listed as 公開中, then cancelled it (中止).
