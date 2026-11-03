## Context

See proposal.md - Why. The current state that shapes the approach:

- **Push offer.** `PushOfferService` (frontend `src/services/push-offer-service.ts`) decides eligibility from `Notification.permission` and the browser's push support, and keeps a per-session flag and a device counter of unanswered offers. My Artists calls it after a saved hype change (`my-artists-route.ts` `offerPush()`), which shows a second snack after the change.
- **Snack bar.** The shared `<snack-bar>` (`frontend/shared/ui/snack-bar/snack-bar.ts`) stacks every snack in the fan app (`replace = false`) with no limit; the organizer console sets `replace` and shows one at a time.
- **Device flags.** Per-page help flags live in `src/adapter/storage/onboarding-storage.ts` (`onboarding.helpSeen:<page>`, cleared by `clearAllHelpSeen()` at sign-in and sign-up). The frontend review rule allows `localStorage` only under `src/adapter/storage/`.
- **Event detail sheet.** `event-detail-sheet.html` renders the hero, the artist, a details section (date, venue), the journey section (two phases of five `role="radio"` buttons and a 「追跡を停止」 button), the All Nearby follow button, and a footer with the official info and calendar links. Each status's label, icon and hue come from `JOURNEY_STATUS_CONFIG` (`src/entities/ticket-journey.ts`), shared with the card badge and the filter chips.
- **Sign-up round trip.** The auth flow already carries application state through the OIDC authorization request (`AuthFlowState` with `flow`, `origin` and `returnTo`, `frontend/shared/services/auth-service.ts`), read back in `auth-callback-route.ts`.
- **Reminders.** `ReminderStage` has only `APPLY_OPEN` (1) and `APPLY_CLOSE_24H` (2); value 4 was `RESULT_DAY` and was removed, and `ticket_sale_reminders.stage` is CHECKed to (1, 2) (backend `internal/entity/ticket_sale_reminder.go`, `schema.sql`). A TicketSale stores no result date, and the Gemini search schema (`internal/infrastructure/gcp/gemini/ticket_sale_searcher.go`) asks only for name, method, start and end.
- **Discovered sales are not proto messages.** `entity/v1/ticket_sale.proto` carries an Organizer's sale only, and `ReminderStage` is backend-internal, so no proto changes.
- **`infer-hype-and-journey`** adds the "set by" of hype levels, `TicketJourneyService.InferTracking`, the calendar-tracking snack and the hype-raise snack. This change rewords both snacks and relies on `SetHype` recording the fan's choice.

## Goals / Non-Goals

**Goals:**
- One place that turns a hype level and a home into place words, used by the hype snack, the hype-raise snack and the out-of-range notice, so all three always say the same thing.
- The result-day reminder reuses the reminder pipeline (scan, sent-log, delivery) with one more stage, not a new job.

**Non-Goals:**
- No change to My Artists' table or its help sheet.
- No proto or RPC change. Every value the new UI shows is already returned by an existing RPC (below).
- No result-day reminder for an Organizer's lottery: the draw already emails the winners.

## Decisions

### Where each new value on screen comes from

| value | screen | read from |
|---|---|---|
| artist name, hype level | My Artists hype snack | `FollowService.List` → `FollowedArtist.artist.name`, `.hype` (already loaded by My Artists) |
| home prefecture for the place words | hype snack, hype-raise snack, out-of-range notice | `UserService.Get` → `User.home.level_1`, mapped to the existing `userHome.prefectures.<key>` short names; for a guest, the guest home in device storage (the fan's own input) |
| push on / off / not offerable | hype snack, push line, out-of-range notice | the browser (`Notification.permission`, `PushManager.getSubscription()`), not a server value; "registered" means this browser has a push subscription |
| whether a concert is matched, its lane | out-of-range notice | `ConcertService.ListByFollower` (proximity) combined with `FollowService.List` hype, as the Dashboard highlight already does (`isHypeMatched`) |
| whether the fan follows the artist | out-of-range notice | the follow store, from `FollowService.List` |
| journey status | ticket section | `TicketJourneyService.List`, via the journey store |

The result date is never shown in the UI; the Applied push line names no date for that reason.

### Hype snack: one helper, one storage key family

- `hypeReachWords(hype, home)` in `src/adapter/view/hype-display.ts`, next to `HYPE_TIERS`, returns 「全て」, 「東京」, 「東京周辺」 or none for Watch. The snack, the hype-raise snack and the out-of-range notice build their text from it and from i18n keys under `hypeReach.*`.
- First-time flags: `onboarding.hypeSnackSeen:<level>` in `onboarding-storage.ts`, written when the push-on or guest form is shown. `clearAllHelpSeen()` is renamed `clearOnboardingSeenFlags()` and removes both prefixes; its callers (sign-in, sign-up completion) are unchanged. Rejected: a server-side flag. It would need a proto field and an RPC for a hint whose loss costs one extra snack.
- The push-offer snack after a hype change goes; `offerPush()` becomes the hype snack, whose action is the offer when eligible and 「設定」 otherwise.

### Push offer: no limits for in-context offers

`PushOfferService` drops the per-session flag and the unanswered counter, and exposes `pushState()`: `on`, `offerable` (undecided and supported) or `settings` (blocked, or a browser that cannot receive push). The device key of the unanswered counter is removed on startup. The post-signup sheet keeps its own once-per-sign-up rule, which never read those values.

### Snack bar: a limit and a replace key

`<snack-bar>` gets a `limit` bindable (fan app shell: 3; organizer console keeps `replace`). Before pushing a snack it dismisses the oldest snacks that dismiss on their own until fewer than `limit` remain; a snack with no auto-dismiss (the update snack) is skipped and not counted. `Snack` options gain `replaceKey`: a new snack with the key of a visible one dismisses it first. My Artists uses `hype:<artistId>`. Rejected: debouncing hype changes, which would delay the feedback of the first tap.

### Event detail sheet

- Markup order: hero, header, date row (with the calendar link moved into it), venue row, out-of-range notice, ticket section (notification button, status row, push line, official site button). The footer goes. The All Nearby follow button stays under the ticket section.
- The five buttons are `<button aria-pressed>`; the radiogroup and its arrow-key handler (`onJourneyKeydown`) go. Pressing the selected button calls the existing `journeyStore.delete`. Rejected: keeping `role="radio"`, which cannot express clearing the selection.
- `JOURNEY_STATUS_CONFIG.tracking.icon` becomes 🔔; the card badge and the filter chip pick it up from the map.
- Out-of-range button: lane `home` → `home`, `near` → `nearby`, `away` → `away`, saved with `followStore.setHype` (recorded as set by the fan under `infer-hype-and-journey`). On success the notice switches to its saved form; the Dashboard highlight follows from the follow store.

### Guest tracking through sign-up

`AuthFlowState` gains `trackEventId`. The guest's button starts sign-up with `returnTo: /concerts/<id>`, `trackEventId: <id>` and a new `AuthStartSource` `ticket_notify`. It does not set `origin: 'event-page'`, so the celebration and the post-signup sheet still run; the sheet's first step asks for push, which the fan has just asked for. After the account is resolved and the guest merge has run, the callback calls `TicketJourneyService.SetStatus(TRACKING)` for that event, then returns to `/concerts/<id>`, which opens the sheet. Rejected: a device-storage flag, which could survive an abandoned sign-up and track the event on a later sign-up from elsewhere; the OIDC state lives only for that one authorization request.

### Result date

- **Storage.** `ticket_sales.result_date DATE NULL`, with `CHECK (result_date IS NULL OR (discovered_at IS NOT NULL AND method = 2 AND result_date >= (sale_end_at AT TIME ZONE 'Asia/Tokyo')::date))`. A calendar date, not a `TIMESTAMPTZ`: pages often give a day or a range of days, and the reminder needs only the day; storing an instant would invent a time. Go entity `TicketSale.ResultDate` (a date value type with a valid flag) and `DiscoveredTicketSale.ResultDate`.
- **Extraction.** The response schema gains an optional `result_date` (`YYYY-MM-DD`): the first day the page says lottery results are announced (当落発表, 抽選結果発表, 当選発表), read in the page's time zone. The searcher drops the field, not the sale, when it is unparsable or before the end date, and reports that as a discard reason in the generation's sale-parse result.
- **Upsert.** On a match, `result_date = COALESCE($new, result_date)`, so a re-discovery without the field keeps the stored date.
- **Pending sales.** `ListWithPendingMilestones` adds `OR result_date >= ((now() - lookback) AT TIME ZONE 'Asia/Tokyo')::date` to the end-time condition.

### Result-day stage

- `ReminderStageResultDay = 4`, reusing the value it had; no row holds 4 today because the CHECK allows only (1, 2), and the migration widens it to (1, 2, 4).
- Anchor: 09:00 on the result date in the fan's time zone; expiry: 22:00 that day, so it never falls into quiet hours and needs no quiet-hours rule of its own. Rejected: the stated announcement time, which many pages do not give; a morning "today" reminder serves both cases.
- Audience: new `TicketJourney.ListUserIDsAppliedSeries`, a repository method beside `ListUserIDsTrackingSeries` with status 2 instead of 1 (backend review rule: a different filter is a different method). The scan calls it only for a discovered Lottery with a result date.
- Content: the `RESULT_DAY` rows of the scan's content table; `DeliverReminder` is unchanged.

### No check-then-act writes

The change adds no write guarded by a separate read. `UpsertDiscovered` keeps its single upsert statement, and the reminder sent-log keeps its unique key on (user, sale, stage).

## Risks / Trade-offs

- [Gemini misreads a result date] → The field is optional and validated against the end date; the integration test against real pages gains result-date cases; a wrong date sends one harmless "results today" push.
- [A result date published after the sale opened is never read] → Discovery searches a series again only when no sale of it is pending. Stated as a follow-up in the proposal.
- [Removing offer limits feels pushy] → The offer appears only on a surface the fan just acted on (a hype change, an event they track), never on launch; the browser prompt still opens only on a tap.
- [Dropping the oldest snack hides an error message] → Error snacks with Retry stay 10 seconds and are rarely stacked with three others; the update snack, the one that must not be missed, is exempt.
- [Spec depends on an unarchived change] → The two snack requirements and "A sign-in from any screen resolves the account with Create" are written against `infer-hype-and-journey`; that change is archived first (see tasks).

## Migration Plan

1. Backend migration: add `ticket_sales.result_date` with its CHECK, and widen `chk_ticket_sale_reminders_stage` to (1, 2, 4). Both are catalog-only changes on small tables. Then deploy the backend; until then nothing writes a result date, and the scan sends no `RESULT_DAY`.
2. Frontend after `infer-hype-and-journey`'s frontend is in production (the reworded snacks replace its texts).
3. Rollback: the column is nullable and unread by older code. Older code treats stage 4 as invalid when it reads the sent-log, so a rollback of the backend deletes the stage-4 rows of `ticket_sale_reminders` first; losing them can at most repeat one result-day push.
