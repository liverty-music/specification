## Why

Three defects of the triage lists (specification#1442, #1443) share their root in what the specs leave unsaid.

- A ticket sale announcement or reminder push for a discovered concert opens `/concerts/<id>`, a page a discovered concert does not have, so the fan lands on a not-found page (backend#893). The notification spec names "the concert page of the fan's linked event" for both types, while the other concert-bound types already send a discovered concert to `/timetable?concert=<id>`.
- A fan whose listing was resold, and not yet refunded, may delete the account: the deletion requirements block only an open Listed listing and say that a listing in any other status does not block. The refund needs no User, but the sold email then reads the deleted User, fails with NotFound and ends in the poison queue (backend#883).
- Deleting an account holds a database connection for its lock and takes a second one for every read and write it makes under the lock, on a production database with about 22 usable connections (backend#882).

## What Changes

- The Notification link requirement states one rule for every type bound to a concert: `/concerts/<id>` when the concert's Series is first-party, `/timetable?concert=<id>` otherwise. ticket_sale_announcement and sales_reminder join it. lottery_loss and concert_cancelled already follow it in code; the spec now says so instead of "the event's page".
- A Sold listing keeps not blocking deletion, and the specs now say what then happens: the refund is made without the User, and the sold email is not sent because the User no longer exists (`SendResaleSold` returns without error, so the announcement is acknowledged instead of retried).
- `UserUseCase.Delete` holds one connection for the whole deletion. This is not a behavioral guarantee of the specs, so it is recorded in the design only.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/notification`: MODIFIED requirement "The link and the grouping tag follow the type" with scenarios for a ticket sale push of a discovered and of a first-party concert.
- `components/usecase/user/delete`: MODIFIED requirement "Delete removes the user" gains the scenario "User with a resold listing awaiting its refund".
- `components/usecase/user/list-deletion-blockers`: MODIFIED requirement "Four kinds of blocker" gains the scenario "Resold listing awaiting its refund".
- `components/usecase/notification/send-resale-sold`: MODIFIED requirement "Sold email after every refunded listing" gains the scenario "Listing's user deleted".
- `components/usecase/notification/send-resale-sold` (Purpose): the sequence diagram gets a `break` after `User.Get` for a user that no longer exists (nothing sent, success). A Purpose is edited in the main spec, not through a delta, so this edit lands with the archive.

The entity operations these usecases rely on are unchanged: `User.Get` (NotFound for an unknown user), `User.Delete`, `ResaleListing.Get`, `ResaleListing.ListByUser`, the Sold status and the refund time of a ResaleListing, and `ResaleListing.RecordRefund`. Only what a caller does with `User.Get`'s NotFound changes.

## Impact

Backend only: `internal/entity/notification_message.go`, `internal/usecase/resale_sold.go`, `internal/infrastructure/database/rdb/user_repo.go` and `traced_pool.go`, with tests. No schema migration and no proto change. The frontend issue frontend#850 (the `/timetable?concert=<id>` deep link opens nothing when the concert is not in the loaded lists) is a separate fix; until it ships, a discovered concert's push opens the timetable without the concert.
