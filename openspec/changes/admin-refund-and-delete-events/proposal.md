## Why

The production test Organizer used by the production E2E suite represents a real Artist, so every test Event names that Artist as its performer, is announced to the Artist's followers and can be opened by anyone with its link. Switching the Organizer to a fictional test Artist needs its existing test Events gone first. Today nothing can remove an Organizer's Event once a fan bought a ticket for it, short of deleting the whole Organizer. The prod E2E suite also keeps adding Orders to its Events, so old test Events will need removing again.

A cancelled real concert needs the same steps: refund every fan, then remove the Event when it is no longer wanted. Today an admin can refund only one Order at a time, by id, with no screen. A refund for 中止 (cancellation) is also accepted for an Event that is still on sale.

While tracing the deletion, two defects turned up:

- Organizer.Delete does not remove ResaleListings. It fails on a foreign key after the Organizer's files and Organization have already been removed.
- An admin's deletion of a Concert also suppresses its slot. A suppressed slot blocks an Organizer from publishing there, with no override, although suppression exists only to keep discovery from bringing a deleted Concert back.

## What Changes

- **Delete an Event that had purchases.** Concert deletion (admin ConcertService.Delete) is refused only while a purchase is still live:
  - an Order that is not Refunded;
  - a Settlement that is not Reversed;
  - a purchase in progress (a Checkout or LotteryEntry whose card authorization is still open, or a Checkout that is Held or Committed).

  Today any Ticket, Order or Settlement blocks it. With the Event, deletion removes its Refunded Orders and their Tickets, Reversed Settlements, ResaleListings, Scanners with their Admissions and RejectedScans, and finished Checkouts and LotteryEntries. A first-party Series left with no Event is removed too. The slot is still suppressed, whatever the Concert's origin.
- **A refund for 中止 needs a cancelled Event.** OrderUseCase.Refund with the reason Cancellation fails with FailedPrecondition unless the Order's Event is CANCELLED. Dispute refunds are unchanged. **BREAKING** for an admin who refunds an Order of an Event that is still PUBLISHED.
- **Admins list the Orders of an Event.** New admin OrderService.ListByEvent.
- **Admins list one Artist's Concerts.** Admin ConcertService.List takes an optional Artist and then returns only that Artist's Concerts, in every state except DRAFT.
- **Admin console:**
  - On the Organizers screen, an admin creates a test Artist (a name only; the music-catalog id is generated) and associates it with the Organizer in one step. Each represented Artist opens a new Artist concerts screen.
  - The Artist concerts screen lists the Artist's Concerts with their state and Paid Orders. A CANCELLED Concert offers **Refund all**, which refunds every Paid Order for 中止 after a confirmation showing their count and total. Every Concert offers **Delete**, after a confirmation.
- **Suppression keeps only discovery away.** Series.PublishEvents, SeriesUseCase.Publish and Series.Update no longer refuse a suppressed slot. An Organizer can publish where an admin deleted a wrong Concert. Discovery still skips a suppressed slot.
- **Organizer.Delete removes ResaleListings** and refuses while a purchase is in progress, because it now removes each Event the same way Concert deletion does.
- **Operations:** the prod test Organizer switches from the real Artist to a fictional test Artist. Its old test Events are cancelled, refunded and deleted, and the prod E2E Events are recreated. A new document describes the prod E2E fixtures.

## Capabilities

### New Capabilities

- `components/entity/order/list-by-event`: Order.ListByEvent returns every Order whose Tickets admit to one Event.
- `components/entity/order/get-event-id`: Order.GetEventID returns the id of the Event an Order is for.
- `components/usecase/order/list-by-event`: OrderUseCase.ListByEvent returns an Event's Orders for an admin.
- `components/infrastructure/admin/web/route/artist-concerts`: the admin console screen listing one Artist's Concerts, with Refund all and Delete.
- `stories/remove-a-cancelled-concert`: an Organizer cancels an Event; an admin refunds every fan and deletes the Event.

### Modified Capabilities

- `components/entity/concert/delete-and-suppress`: removes a cancelled Event's refunded purchases, resale listings and scanner records with it, and an emptied first-party Series. It is refused only by a live purchase.
- `components/entity/concert/list`: takes an optional Artist to narrow the catalog.
- `components/entity/event/get`: also returns the Event's publish state.
- `components/entity/organizer/delete`: removes ResaleListings and refuses while a purchase is in progress.
- `components/entity/series/publish-events`: a suppressed slot no longer blocks a publish.
- `components/entity/series/update`: a suppressed slot no longer blocks a new start time.
- `components/usecase/concert/delete`: the blocking condition follows Concert.DeleteAndSuppress.
- `components/usecase/concert/list`: passes the optional Artist through.
- `components/usecase/order/refund`: the reason Cancellation requires a CANCELLED Event.
- `components/usecase/series/publish`: a suppressed slot no longer fails the publish.
- `components/adapter/admin/api/rpc/concert`: List accepts an optional Artist.
- `components/adapter/admin/api/rpc/order`: adds ListByEvent.
- `components/infrastructure/admin/web/route/organizers`: creates a test Artist, and opens a represented Artist's concerts.
- `stories/delete-a-wrong-concert`: a deleted slot stays deleted for discovery only.
- `components/entity/suppressed-concert` (Purpose): suppression keeps discovery, not Organizer publishing, from bringing a slot back.
- `stories/delete-a-wrong-concert` (Purpose): SeriesUseCase.Publish leaves the usecase diagram.

Unchanged, and relied on:

- `components/usecase/artist/create`: an MBID the music catalog does not know registers the Artist under the given name. The test Artist relies on this.
- `components/usecase/organizer/associate-artist` and `components/usecase/organizer/disassociate-artist`: they switch the Organizer's Artist.
- `components/usecase/series/cancel` and `components/entity/series/cancel-events`: they cancel the Events before the refund.
- `components/usecase/organizer/delete`: unchanged. It calls Organizer.Delete, whose promise changes above.
- `components/entity/order/get`, `components/entity/order/commit-refund` and `components/entity/order/create-refund`: Refund keeps using them as they are.
- `components/adapter/admin/api/rpc/artist`: Create is already served on the admin console with the admin role.

## Impact

- **specification:**
  - `rpc/admin/order/v1`: `ListByEvent`.
  - `rpc/admin/concert/v1`: `ListRequest.artist_id` (optional).
  - Comments on `OrderService.Refund` and `ConcertService.Delete`.
  - The change is additive in proto.
- **backend:**
  - Concert deletion and Organizer deletion share one per-Event removal.
  - Order.ListByEvent and Order.GetEventID.
  - Event.Get returns the publish state.
  - Refund checks the Event state.
  - The suppression checks leave the Series publish and update paths.
  - Concert.List takes the optional Artist.
  - Admin handlers and integration tests.
- **frontend (admin console):**
  - The Organizers screen gets test-Artist creation and a link per represented Artist.
  - The new Artist concerts screen.
- **cloud-provisioning:** none.
- **Operations (prod):**
  1. Create and associate the test Artist.
  2. Cancel the old test Events in the organizer console.
  3. Refund all and delete them in the admin console.
  4. Remove the real Artist from the Organizer and unfollow it with the E2E fan.
  5. Recreate the E2E Events and rerun the prod E2E suite.
  6. Write `frontend/docs/prod-e2e-fixtures.md`.
- **Follow-up issues, not in this change:**
  - Cancelling an Event leaves its open lottery entries and held checkouts with their card authorizations.
  - Fans get no notice of a refund.
  - The Organizer.Delete spec both removes and refuses on a payout-account record.
