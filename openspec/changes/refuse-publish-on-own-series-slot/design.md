## Context

- `SeriesRepository.PublishEvents` (`backend/internal/infrastructure/database/rdb/series_events_repo.go`, the switch after `checkSlot`) decides each draft date by the Event holding its slot:
  - none: publish the draft;
  - CANCELLED: FailedPrecondition;
  - another Organizer's Event: FailedPrecondition;
  - this Series' Event: drop the draft;
  - anything else: claim it with `claimEventQuery` (`UPDATE events SET series_id = $2, publish_state = 'PUBLISHED' ...`).
- The last case is meant for discovered Events. The original design only claimed those (archive `2026-08-28-organizer-event-authoring` design D4). Because the check only refuses *another* Organizer, the same Organizer's other Series fall into it. Commit d005c7d1 then wrote that behavior into the spec, and `2026-10-13-restructure-event-publishing` kept it (its Non-Goals). The same design's Assumption 4 already calls publish "narrower" than `Series.Update`, which refuses any first-party Event at a new start time's slot (`components/entity/series/update` "A new start time takes its slot").
- What a first-party Event carries that a claim leaves behind:
  - `ticket_sales.series_id` and `seat_types.series_id` point at the old Series;
  - `ticket_stocks.seat_type_id` and `ticket_sale_events.event_id` point at the moved Event;
  - visibility belongs to the Series.

  So a claimed Event ends up sold by another Series' sale, stocked with another Series' seat types, and shown with the new Series' visibility.
- The organizer console turns every publish failure into the snackbar `event.publishFailed` (公開できませんでした):
  - `organizer/concert/concert-route.ts` `publish()`: no retry;
  - `organizer/event/event-route.ts` `publish()`: with 再試行.

  A refused slot fails the same way on every retry.
- No RPC in the project returns Connect error details (no `errdetails` / `ErrorInfo` in backend or frontend).

## Goals / Non-Goals

**Goals:**
- Publish never moves a first-party Event between Series.
- A member whose publish is refused learns what to change, without a retry that cannot succeed.

**Non-Goals:**
- Moving a date to another Series, or changing visibility after the first publish (proposal, Out of scope).
- Repairing the Events moved on 2026-10-30; they are test data and are retired (D4).
- Naming the concert that holds the slot (D3).

## Decisions

### D1. Claim only an Event whose Series has no Organizer

The switch in `PublishEvents` refuses any slot holder that has an Organizer and is not this Series. The cases, in order:
1. no holder → publish;
2. CANCELLED → FailedPrecondition (unchanged);
3. this Series → drop the draft (unchanged);
4. a holder with an Organizer → FailedPrecondition. One message covers both another Organizer and the same Organizer, "the event's slot is held by another series' event", and the log keeps `holder_event_id`;
5. otherwise (a discovered Event) → claim.

The `organizerID == nil` branch (publishing a discovered Series) needs no special handling: case 4 refuses any first-party holder.
- `claimEventQuery`'s `COALESCE(per_account_limit, $3)` and its comment about "an event of another series of the organizer" lose their second case. The comment is reduced to the discovered case, and the COALESCE stays, because a discovered Event has no limit.
- **Why:** this is the same rule `Series.Update` applies to a new start time, so the two paths that put a date on a slot agree. It is also the original D4 intent.
- **Rejected:** claim only when the held Event has no sales or stocks. Visibility would still move, and the rule would depend on how far the other concert's sales have progressed.

### D2. Concurrent publishes of the same slot

Not new, but checked because D1 is a check-then-act. `PublishEvents` locks this Series and its Events (`lockSeriesForWrite`, `lockSeriesEvents`), not the slot. Two Series publishing the same slot at once can both see no holder. The second `UPDATE ... publish_state = 'PUBLISHED'` then violates the partial unique index `uq_events_natural_key` (non-DRAFT rows) and the transaction rolls back. No Event moves in that race, which is the property D1 needs. The error code of that rare race is not changed here.

### D3. The console says why, without naming the other concert

On `ConnectError` with `Code.FailedPrecondition` from `Publish`, both routes:
- show a new snackbar key, ja: 「同じ会場・日時の公演日がほかの公演にあるか、中止した公演日があるため公開できませんでした。公演の編集で日付か開始時刻を変えてください」;
- offer no retry;
- reload the page's dates (`load()` on the concert page, `page.reload()` on the event page).

Any other error keeps `event.publishFailed` and the current retry behavior.
- **Why one message:** every slot refusal (another Organizer, own other concert, cancelled date) has the same fix, a different date or start time. A message naming the holding concert would need an error detail on the RPC, which the project has nowhere. It also must not name another Organizer's concert.
- **Other FailedPrecondition causes of `Publish`:**
  - a blank title, no performer, or a date without venue or date, which the editor's own validation stops before a draft can be published (to be confirmed in task 4.1);
  - a date that is no longer DRAFT, for a page opened before another member published it. The reload then shows it published.

  The message is about the slot because that is the cause a member can reach from a valid page.
- **Rejected:** keep 再試行 on the event page for FailedPrecondition. It never succeeds.

### D4. Retire the Events moved on 2026-10-30, do not repair them

The affected Series are the e2e-test Organizer's:
- "E2E Sale 1030", "E2E Referral 1030" and "E2E Resale 1030b", which hold moved Events;
- the Series they took the Events from, which are now eventless or reduced. "E2E Resale" (`01a16e28-c6bd-…`) is shown as a draft.

They are retired the way `frontend/docs/prod-e2e-fixtures.md` "Retiring used Events" describes (console 公演を中止, admin `Refund all`, `Delete`), skipping any Event that `.auth/prod-e2e.env` still names. Putting the Events back would need hand-written SQL in production for test data. This is a one-time action through the existing consoles, so it is not Pulumi.

### D5. Proto comment only

The `Publish` doc comment in `organizer/series/v1/series_service.proto` changes:
- it drops "(or an Event of another series of the same Organizer)";
- it lists "held by another Organizer's or another of this Organizer's series' Event";
- it drops "is suppressed" from the FAILED_PRECONDITION list. A suppressed slot does not block a publish (`components/entity/series/publish-events` "Suppressed slot"), so that line was wrong.

There is no wire change, so no `buf skip breaking` label is needed. The frontend does not have to wait for a BSR release: the console change does not depend on generated types.

## Risks / Trade-offs

- [An Organizer has a real reason to re-home a date to a new concert] → Not supported; decided 2026-10-31 that it is not needed now. The member picks a different start time, or cancels the old date first. A cancelled date also blocks its slot (`Cancelled slot`), so re-using the exact slot is not possible either way. This is the existing rule for cancelled dates.
- [The slot message appears for a stale-page FailedPrecondition] → The page reloads and shows the date's real state; the case needs two members publishing the same draft at once.
- [The members' guide quotes console words] → Task 4.3 checks the chapter 公演をつくって公開する and `test/organizer/guide.spec.ts`.

## Migration Plan

1. The specification PR: deltas plus the proto comment.
2. The backend PR, then a release. From then on the refusal is live in production.
3. The frontend PR (console message, fixtures doc), merged after the backend release so the new message has a refusal to show. It is harmless earlier: the message only replaces the generic one for an error code that already exists.
4. Retire the 2026-10-30 Series (D4).

Rollback: revert the backend release; publish claims own Events again.
