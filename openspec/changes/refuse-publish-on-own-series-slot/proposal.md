## Why

Publishing a draft date whose venue, date and start time match a date of another of the same Organizer's Series moves that date, with its sales, seat-type stocks, orders and visibility, into the new Series. On 2026-10-30 this made an UNLISTED date of the e2e-test Organizer public without anyone touching it (backend#737). The claim at publish exists to absorb discovered Events, which own nothing; extending it to the Organizer's own Events came from the first implementation and was then written into the spec as shipped behavior, while the start-time rule of `Series.Update` already refuses the same overlap "so no Event with sales is ever merged away".

## What Changes

- Publish claims only a discovered Event at a draft date's slot. A slot held by an Event of any other first-party Series, the Organizer's own included, fails the publish with FailedPrecondition and nothing is published, as a slot held by another Organizer or by a CANCELLED Event already does. **BREAKING** for a caller that relied on moving its own date to another Series by publishing.
- The organizer console tells the member why a publish was refused and does not offer a retry that cannot succeed: today every publish failure shows 公開できませんでした with 再試行.
- The `Publish` doc comment in the organizer Series proto drops the same-Organizer claim and the wrong statement that a suppressed slot fails the publish.

Out of scope: an explicit way to move a date to another Series, or to change a concert's visibility after its first publish (decided 2026-10-31: not needed now).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/series/publish-events`: "Draft events become published" claims discovered Events only; "Blocked slots fail the whole publish" adds a slot held by another first-party Series of the same Organizer.
- `components/usecase/series/publish`: "Draft becomes live" fails on a slot held by any other first-party Series. The entity operation it relies on is `components/entity/series/publish-events`, listed above.
- `components/infrastructure/organizer/web/route/concert`: "Publish or cancel the concert's dates together" says why a publish was refused.
- `components/infrastructure/organizer/web/route/event`: "The event header and its actions" says why a publish was refused.

`stories/publish-an-organizer-concert` is unchanged: its "Published concert takes over discovered data" already speaks of discovered Concerts only.

## Impact

- **specification**: the `Publish` doc comment in `proto/liverty_music/rpc/organizer/series/v1/series_service.proto` (comment only, no wire change).
- **backend**: the slot check of `PublishEvents` in `internal/infrastructure/database/rdb/series_events_repo.go`, the `PublishEvents` doc in `internal/entity/series.go`, and the publish tests in `series_events_repo_test.go` and `usecase/series_lifecycle_uc_test.go`.
- **frontend**: publish error handling in `organizer/concert/concert-route.ts` and `organizer/event/event-route.ts`, the organizer locale files, and the members' guide chapter 公演をつくって公開する if it describes a refused publish; `docs/prod-e2e-fixtures.md`'s slot warning, which describes the takeover.
- **Production data**: the e2e-test Organizer's Series affected on 2026-10-30 keep Events whose sales and stocks belong to another Series. They are test data; they are retired, not repaired.
