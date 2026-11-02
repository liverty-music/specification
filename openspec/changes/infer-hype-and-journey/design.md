## Context

See proposal.md - Why. The current state that shapes the approach:

- `followed_artists.hype` is `TEXT` with a CHECK and defaults to `'nearby'` (backend `schema.sql`); the proto exposes it as `HypeType`. `ticket_journeys.status` is `SMALLINT` (1-5). Neither table records who set the value.
- The only journey the platform writes today is Paid: `orderPaidConsumer` calls `TicketJourneyUseCase.MarkPaid` (backend `internal/adapter/event/order_paid_consumer.go`), from the `ORDER.paid` announcement through its own durable consumer (cloud-provisioning `consumer-mark-ticket-journey-paid.yaml`). A lottery entry writes no journey, and after `publish-events-through-outbox` LotteryEntry.Create still announces nothing (that change's design, "Subjects after this change").
- A User's home is optional today: `users.home_id` is nullable with `ON DELETE SET NULL` (backend `schema.sql`), and User.Create stores a User without one. The Dashboard opens the home sheet whenever the signed-in fan has no home, but the sheet is closable outside onboarding (`required.bind="isOnboarding"` in `dashboard-route.html`), and the auth callback ends onboarding on every sign-in (`auth-callback-route.ts`). A guest who signs up from an event page never sees the sheet before the account is created, and My Artists works without a home.
- The rule "which hype level matches which concert" already lives on the entity: `Hype.MatchingConcerts(home, concerts)` with table tests in `internal/entity/follow_test.go`.
- The event detail sheet's add-to-calendar link is a Google Calendar web URL opened with `target="_blank"` (frontend `event-detail-utils.ts`), so the fan leaves the app's view: a new tab, or the Google Calendar app on a phone.
- `publish-events-through-outbox` moves every analytics signal of these operations into the entity operations' own announcements (written in the same transaction through the outbox). That change is archived; this change is written on its model (proposal.md - Capabilities).
- Guest follows live in `localStorage` (`guest.followedArtists`) and are merged at sign-up; today the merge sends only levels that differ from Nearby, so a guest's chosen Nearby is lost (a known limitation stated in `stories/merge-guest-data-on-signup`).

## Goals / Non-Goals

**Goals:**
- One concept, "set by", for both values, stored next to the value it describes.
- Every rule that decides whether the app may change a value is a pure function on the entity, covered by table tests.
- A fan's own write and the app's write to the same Follow never race into the app's value winning.

**Non-Goals:**
- No new screen and no change to My Artists. Who set a level is not shown to the fan.
- No timestamps on either table (`scripts/lint-schema.sh` rejects audit columns). How often values are set, and by whom, is measured from the announcements in product analytics.
- No screen reads who set a value, so the fan's view `FollowedArtist` does not carry it.

## Decisions

### Storage: `hype_set_by` and `status_set_by`, `TEXT` with a CHECK

```sql
ALTER TABLE followed_artists ADD COLUMN hype_set_by TEXT NOT NULL DEFAULT 'default'
  CONSTRAINT chk_followed_artists_hype_set_by CHECK (hype_set_by IN ('default', 'fan', 'inference'));
ALTER TABLE ticket_journeys ADD COLUMN status_set_by TEXT NOT NULL DEFAULT 'fan'
  CONSTRAINT chk_ticket_journeys_status_set_by CHECK (status_set_by IN ('fan', 'platform', 'inference'));
```

- **Name.** "set by default / by the fan / by inference / by the platform" reads as plain English, and one name serves both tables. Rejected: `source` (in this codebase "source" is the external page a concert was found on: `source_url`, `event.sourceUrl`); `origin` (used for where a Series came from); `explicit` (in English it often means adult content); a boolean `hype_chosen` (does not say who chose, and could not tell an inferred level from the default without relying on the default staying Nearby).
- **Type.** `TEXT` with a CHECK, like `hype` in the same feature and like 18 of the 21 closed value sets in `schema.sql`. The storage type does not depend on the API: `hype` is `TEXT` in the database and `HypeType` in proto, mapped in the repository. The value set only grows, so an enum type would also work; CHECK keeps one style for the feature.
- **Backfill.** `hype_set_by = 'fan'` where `hype <> 'nearby'`, else `'default'` (a level other than the starting one can only have come from the fan). Every existing journey becomes `'fan'`, so no inference ever replaces it.
- **Migration safety.** A constant default makes `ADD COLUMN ... NOT NULL DEFAULT` a catalog-only change. Both tables are small (hundreds of rows), so the backfill `UPDATE` and the CHECK validation run in one migration without batching.

### Proto: the entity messages carry who set the value

After `publish-events-through-outbox`, an announcement's payload is the entity's proto message (`Follow` for the ARTIST subjects, `TicketJourney` for the journey subject), and the analytics consumer maps it to the catalogue event. Who set the value therefore has to be on those messages, or analytics never sees it:

```proto
// entity/v1/follow.proto
enum HypeSetBy { HYPE_SET_BY_UNSPECIFIED = 0; HYPE_SET_BY_DEFAULT = 1; HYPE_SET_BY_FAN = 2; HYPE_SET_BY_INFERENCE = 3; }
message Follow { /* 1-3 unchanged */ HypeSetBy hype_set_by = 4 [(buf.validate.field).required = true, (buf.validate.field).enum.defined_only = true]; }

// entity/v1/ticket_journey.proto
enum TicketJourneyStatusSetBy { TICKET_JOURNEY_STATUS_SET_BY_UNSPECIFIED = 0; TICKET_JOURNEY_STATUS_SET_BY_FAN = 1; TICKET_JOURNEY_STATUS_SET_BY_PLATFORM = 2; TICKET_JOURNEY_STATUS_SET_BY_INFERENCE = 3; }
message TicketJourney { /* 1-3 unchanged */ TicketJourneyStatusSetBy status_set_by = 4 [(buf.validate.field).required = true, (buf.validate.field).enum.defined_only = true]; }
```

Two enums, not one shared `SetBy`: each field has its own closed set (a hype level is never set by the platform, a journey never by default), and `defined_only` then rejects the impossible values. `TicketJourneyService.List` returns `TicketJourney`, so the fan's own journeys carry the field too; the frontend ignores it. Adding fields is not a breaking change for `buf breaking`.

### Entity rules in Go

On `entity.Hype` and `entity.Follow` (backend `internal/entity/follow.go`), beside `MatchingConcerts`:

- `Hype.IsAbove(other Hype) bool`: the order Watch < Home < Nearby < Away.
- `LowestHypeMatching(home *Home, c *Concert) (Hype, bool)`: the lowest level whose `MatchingConcerts(home, []*Concert{c})` includes `c`, and false when the concert is outside the home area and its distance cannot be measured (no venue coordinates or no home centroid). `ProximityTo` returns Away for such a concert too, but an unknown location says nothing about how far the fan travels, so it must not raise a level to Away (entity spec "The lowest hype level that matches a concert").
- `(*Follow).RaisableTo(h Hype) bool`: `HypeSetBy != SetByFan && h.IsAbove(f.Hype)` (entity spec "The app may raise only a hype level the fan did not set").
- `HypeSetBy` and `TicketJourneySetBy` are string types with constants, validated like `Hype`.

The usecases only load, ask these functions, and save.

### `Follow.RaiseHype`: check and write under one row lock

`followRepo.RaiseHype(ctx, userID, artistID, hype)` runs one transaction: `SELECT hype, hype_set_by ... FOR UPDATE`, then `RaisableTo` in Go, then `UPDATE ... SET hype = $3, hype_set_by = 'inference'` and the outbox announcement. No row means NotFound.

- **Lock.** The rows read and written are the one `followed_artists` row of the fan and the artist. `Follow.SetHype` updates the same row, so its `UPDATE` waits for, or is waited on by, the `FOR UPDATE`. If the fan's SetHype commits first, RaiseHype reads `hype_set_by = 'fan'` and changes nothing. If RaiseHype commits first, the fan's SetHype then overwrites it as set by the fan. In neither order does the app's level replace the fan's.
- Rejected: one conditional `UPDATE ... WHERE hype_set_by <> 'fan' AND <rank> < <rank>`. It is atomic without a transaction, but it repeats the rule in SQL, where the entity table tests do not cover it.

### `TicketJourney.UpsertIfReplaceable`: one guarded write for the platform and the app

`journeyRepo.UpsertIfReplaceable(ctx, userID, eventID, status, setBy)` runs one transaction: `INSERT ... ON CONFLICT (user_id, event_id) DO NOTHING RETURNING ...`; when a row was inserted, it announces and returns `stored = true`. Otherwise it reads the row with `SELECT ... FOR UPDATE`, asks `(*TicketJourney).ReplaceableBy(status, setBy)` in Go, and on `true` updates and announces.

- **One rule, one place.** `ReplaceableBy` is the entity requirement "Which journeys the platform and the app may replace": inference replaces nothing; Applied by the platform replaces Tracking, Applied and Lost, not Unpaid or Paid. Both InferTracking and MarkApplied use this operation, so there is no second guarded write.
- **Lock.** The insert's conflict on the primary key, or the row lock, serializes it with the fan's `Upsert`. A journey the fan stores a moment earlier is read and kept.
- **Why Applied must not replace Unpaid or Paid.** Receivers do not rely on order across subjects (outbox design, "Ordering across subjects"). If the forwarder is delayed, `ORDER.lottery_entry_entered` can arrive after `ORDER.paid` of the same fan and event; an unconditional Upsert would move a Paid journey back to Applied.
- **Why it replaces Lost.** A fan who lost a presale and enters the general lottery for the same event has entered again.
- `Delete` removes the row, so a later calendar add can store Tracking again (the decision "infer again after undo").
- Rejected: `TicketJourney.Create` (store only when no journey exists) for MarkApplied. A fan whose calendar add started Tracking would never get Applied from their entry.
- MarkPaid keeps the unconditional `Upsert`: Paid is a fact that replaces every status.

### Raising the hype level: one helper shared by two usecases

`TicketJourneyUseCase.SetStatus`, `TicketJourneyUseCase.MarkPaid` and `TicketJourneyUseCase.MarkApplied` run the same steps after their journey write. A usecase must not call another usecase interface, so the steps live in an unexported helper of the `usecase` package (`raiseHypeToMatch(ctx, users, concerts, follows, userID, eventID)`), not in an interface method:

1. Skip unless the status is Applied, Unpaid or Paid.
2. `User.Get` → the fan's home.
3. `Concert.ListByIDs([eventID])` → skip when the event is not a concert.
4. `Follow.ListByUser` → the Follows of the concert's artists; skip unless exactly one.
5. `LowestHypeMatching` (skip when there is none) → `RaisableTo` → `Follow.RaiseHype`.

Every failure is logged at Warn and swallowed: the journey write already succeeded and is what the caller asked for. MarkPaid and MarkApplied therefore are not retried for a failed raise. MarkApplied runs the helper only when UpsertIfReplaceable stored Applied.

The fan's own SetStatus raises in the same request, not from the `TICKET_JOURNEY.status_changed` announcement, so the sheet can show the raise snack with its undo right after the save. A failed raise does not fail the save, so the fan's main action is never affected.

- **One followed performer only.** A fan who enters a festival lottery shows they will travel for the festival, not for each performer. With two or more followed performers the app cannot tell which artist moved the fan, so it raises none.
- **Every fan has a home** ("Every User has a home" below). Without one, every concert's lowest matching level would be Away and the app would raise every artist the fan tracks. If `User.Get` returns a User without a home (only before the NOT NULL migration), the helper skips.
- **Target in practice.** A level not set by the fan is Nearby (default) or Away (inference), so a raise always goes from Nearby to Away. The snack copy 「遠方の新着ライブも通知します。」 depends on this; if the starting level ever changes, that copy must change with it.

### Platform writes come from announcements

Both platform writes run in consumers, outside the transaction of the fact they follow:

| Fact | Announced by | Subject | Receiver |
|---|---|---|---|
| a new lottery entry | LotteryEntry.Create, in the transaction that stores the entry and its Pending Order | `ORDER.lottery_entry_entered` (new), payload the Pending Order (it names the entry, the user and the TicketStock) | TicketJourneyUseCase.MarkApplied |
| a paid Order | Order.Issue | `ORDER.paid` (exists) | TicketJourneyUseCase.MarkPaid (exists) |

- **Why not in Confirm.** The entry and its card authorization are the fan's money; the journey is a record about them. A journey write inside Confirm would make Confirm depend on the journey table and on the follow reads of the raise. From the announcement, a failure retries in the consumer and Confirm never sees it.
- **Name.** `lottery_entry_entered` follows `ORDER.lottery_entry_drawn`: the entry's event, in the past tense, under `ORDER.*`. The `ORDER` stream captures it with its wildcard (cloud-provisioning `stream-order.yaml`, `subjects: ["ORDER.*"]`); MarkApplied gets its own durable consumer, as MarkPaid has `consumer-mark-ticket-journey-paid.yaml`.
- **Payload.** The Pending Order, because the LotteryEntry message names neither the user nor the event (`entity/v1/lottery_entry.proto`: id, order id, ticket sale id, state). The receiver reads the event of the Order's TicketStock, as MarkPaid does.
- **Repeats.** A redelivered announcement runs MarkApplied again; UpsertIfReplaceable finds Applied set by the platform and stores nothing, so the status change is not announced twice and no raise runs (the same rule as Upsert, which announces nothing when the status and set by do not change).
- **Late announcements.** MarkApplied reads the entry with `LotteryEntry.Get` and records nothing once the entry is no longer Entered. An announcement held back by the forwarder until after the draw therefore cannot move a Lost, whether the fan set it or a later draw records it, back to Applied. Rejected: putting the entry id on the journey to recognize a repeat; the entry's own state already says whether the entry is still open.
- Lost for a lost entry is a follow-up after `make-lottery-draw-durable` replaces `RunDraw`.

### Every User has a home

The entity attribute `home` becomes required: chosen when the User is created, changed with SetHome, never removed.

- **Backend.** `User.Create` fails with InvalidArgument without a Home. This rule ships in the second backend release, with the NOT NULL migration, after the frontend that asks for the home is live (Migration Plan). `UserUseCase.Create` keeps its role as the one call for both a new and a returning identity: with no Home it looks the identity up and returns the existing User, or fails with FailedPrecondition when there is none. The RPC request keeps `home` optional, because a returning fan's sign-in sends none; the doc comments say a new identity needs it.
- **Frontend.** The auth callback calls Create as today. On FailedPrecondition it opens the `user-home-selector` in the mode that cannot be closed (the existing `required` bindable), calls Create again with the chosen home and continues to the return URL (the event page, for a sign-up there). The guest's home from onboarding is sent as today, so a guest who chose a home never sees the sheet. The Dashboard's branch that opens a closable sheet for a signed-in fan without a home goes.
- **Database.** `ALTER TABLE users ALTER COLUMN home_id SET NOT NULL` fails while any row has no home, so it is a second migration, applied after a read-only check finds no such row. The foreign key changes from `ON DELETE SET NULL` to `ON DELETE RESTRICT`: a home is never deleted on its own, and SET NULL would contradict NOT NULL.
- **Rows without a home.** Accounts created before this change may have none. Each is signed in once and given a home in Settings, or deleted, before the second migration. Until then the raise helper skips a fan without a home.
- **End-to-end test fans.** Their Users are created through the same callback, so the Playwright sign-up helpers choose a home in the sheet.
- Rejected: a sheet in the app shell that blocks every screen for a signed-in fan without a home. After the second migration no such fan exists, so it would be code for rows that a one-time check removes.

### RPC: `TicketJourneyService.InferTracking`

```proto
rpc InferTracking(InferTrackingRequest) returns (InferTrackingResponse);
message InferTrackingRequest { liverty_music.entity.v1.EventId event_id = 1 [(buf.validate.field).required = true]; }
message InferTrackingResponse { bool started = 1; }
```

A domain verb (`rpc-design` skill): the method states what the server does with a fan's action, and the server applies the rule. Rejected: a `set_by` field on `SetStatusRequest`. It would let one method change its write rule by a flag, and a client could claim `platform`.

### Screens: where each value comes from

| Screen value | Read from |
|---|---|
| Tracking after a calendar add | `InferTrackingResponse.started`; on `true` the journey store sets Tracking for the event, as it does after `SetStatusResponse` |
| No status after undoing an inferred Tracking | `TicketJourneyService.Delete` succeeded |
| The raised level in the snack and on My Artists | `FollowService.List` → `FollowedArtist.hype`, re-read after a saved Applied, Unpaid or Paid when the concert's card was not matched before the save |
| Highlight on the Dashboard after a raise | the same re-read; the follow store's new level feeds the existing matched computation |
| The level after undoing a raise | `FollowService.SetHype(previous)` succeeded |

The previous level for the undo is the level the follow store held before the re-read, which came from `FollowService.List` too. The re-read bypasses the session cache of `ListFollowed` results.

### The calendar snack waits for the fan to come back

The sheet calls `InferTracking` on the click, before the browser leaves, so the journey is saved even if the fan never returns. On `started`, it registers a one-shot `visibilitychange` listener and shows the snack when `document.visibilityState` becomes `visible`; if the page did not become hidden within 1 second of the click, it shows the snack at once. The listener is released in `detaching()`. Rejected: writing on return. A fan who closes the calendar app and never comes back would lose a signal the click already gave.

### Guest storage

A guest follow entry gains `hypeSetBy: 'default' | 'fan'`. A hype change by the guest sets `'fan'`. An entry without the field is read as `'fan'` when its hype differs from Nearby, else `'default'`, matching the server backfill. The merge calls `FollowService.SetHype` for every entry set by the fan, including Nearby.

### Analytics

`artist.hype.changed` and `ticket.journey.status.changed` gain the property `set_by`, which the analytics consumer reads from the payload's `hype_set_by` or `status_set_by`. The event catalog (`docs/analytics/event-catalog.md`) documents it. No new event.

## Risks / Trade-offs

- [A raise to Away sends the fan more pushes than they asked for] → only after the fan's own Applied, Unpaid or Paid for a distant concert, never from Tracking or a guess, and the sheet offers undo at once. The undo is the fan's choice and stops further raises for that artist.
- [A fan who records Applied outside the sheet (none today) gets no snack] → the raise still happens and My Artists shows it; acceptable while the sheet is the only place.
- [The calendar add is a weak signal: some fans add concerts they will not try to get] → Tracking only adds sale notices, the snack offers undo on return, and `status_set_by = 'inference'` lets analytics measure how often inferred Tracking is undone.
- [The return detection misses some browsers that do not fire `visibilitychange` when a new tab opens] → the 1-second fallback shows the snack at once; the journey is saved either way.
- [A PWA that still runs a frontend from before step 4 after step 6] → its sign-up without a home fails with FailedPrecondition until it updates to the new frontend. No account is created without a home, so no row needs fixing.
- [A sign-up now has one more step for a guest without a home] → only guests who skipped onboarding (an event page, a shared link) see it, and the step is the same sheet onboarding uses. The account cannot be created without it, which is the intent.
- [The two journey writes from announcements lag behind the fact] → the fan sees Applied after the forwarder and the consumer run (seconds). The lottery entry screen shows the entry itself, not the journey.
- [Overlap with in-flight changes] → written against the main specs as the archived `publish-events-through-outbox` left them. `make-lottery-draw-durable` adds a requirement to `stories/win-tickets-in-a-lottery` under a different name, so the two deltas do not collide.
- [Verification without a dev environment] → unit and repository tests, the Stripe Sandbox E2E for the lottery entry (Applied after the entry is announced), and read-only prod checks of the new columns, the NOT NULL home and the announcements.

## Migration Plan

1. specification: proto `InferTracking`, `Follow.hype_set_by`, `TicketJourney.status_set_by`, the `UserService.Create` comments and the event catalog; release; BSR generation.
2. cloud-provisioning: the durable consumer of `ORDER.lottery_entry_entered` for MarkApplied, before the backend that announces it.
3. backend: Atlas migration (columns, backfill, CHECK); entity, repositories, the new subject and its receiver, usecases, handler. Old frontends keep working: they never call `InferTracking`, and `SetHype`, `SetStatus` and `UserService.Create` keep their requests and rules.
4. frontend: the home sheet at sign-up, guest storage and merge, calendar inference, raise snack.
5. Read-only check that no `users` row has no home (after signing in and setting a home for, or deleting, any such account).
6. The second backend release: the home rule of `User.Create` and `UserUseCase.Create`, and the migration making `home_id` NOT NULL with the foreign key `ON DELETE RESTRICT`. The frontend of step 4 already handles FailedPrecondition, so no sign-up fails in between.

Rollback: revert the backend release; the new columns stay and are ignored (their defaults keep inserts valid). Dropping them is a separate migration, needed only if the change is abandoned. After step 6, a reverted backend that creates a User without a home fails on the NOT NULL; revert the second migration first.
