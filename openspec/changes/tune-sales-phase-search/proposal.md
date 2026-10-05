## Why

Sales-phase discovery has cost Gemini grounding queries every day without delivering anything: in 2026-09 it spent about ¥4,200 for 60 new phases, no fan tracks any series in prod, and no reminder has ever been sent. A check of those 60 phases against the official pages found 58% accurate and 8% wrong (a year off, a sale that does not exist, another show's sale). Only 23% were found before their application opened, so most phases could not be acted on. A local evaluation on gemini-3.8-flash with a single JSON call, required fields and only not-yet-opened sales gave 15 of 15 values correct (13 of 15 sales found) at about 10 search queries per call. The reminder copy also has defects: it never names the tour, it says "24 hours left" after a quiet-hours deferral, and it shows the ticketing service instead of "fan club" for fan-club presales.

## What Changes

- **BREAKING** A Sales Phase keeps only series, method (now required: `LOTTERY` or `FIRST_COME`), apply start time, apply end time (required for a lottery), lottery result time and discovered time. Channel, provider name, sequence, payment deadline time, url and the `UNSPECIFIED` method are removed from the entity, the proto message and the database.
- Search returns only sales whose application has not started yet, in one grounded gemini-3.8-flash call that returns JSON (thinking `low`, temperature not sent, Google Search limited to the last 30 days). The XML envelope and the flash-lite parse step are removed. Ticket trades and resales are excluded. A first-come sale without a stated end ("until sold out") is returned.
- Search is no longer best-effort on failure. An empty response, an invalid response or a rejected request (including the 429 spend cap) fails the search, so the next daily run searches again.
- Discovery searches a series only when all of these hold:
  - a fan tracks it
  - it has an event that has not ended (the 90-day limit is removed)
  - it has no stored phase whose application has not ended
  - it was last searched 30 or more days ago

  A first-come phase without an end counts as ended once it opens. The last search time is recorded per series.
- Upsert treats phases with the same series, method and apply start date (Japan time) as one phase.
- Reminders depend on the method:
  - first-come: one reminder 30 minutes before the sale opens
  - lottery: one when applications open, one 24 hours before they close, and one on the result day

  The 1-hour-before-close stage and the 21:00 pre-quiet fallback for close stages are removed. A first-come reminder that would fall in quiet hours moves to 21:00 the evening before.
- The announcement and the reminders name the date, the method and the tour, using fixed Japanese and English copy, with the tour name on a new line at the end. Tapping either opens the event sheet of the earliest upcoming event of the series that the recipient tracks.

## Capabilities

### New Capabilities

- `components/entity/sales-phase-search-log`: when each series was last searched for sales phases.
- `components/entity/sales-phase-search-log/list-by-series`: read the last search time of given series.
- `components/entity/sales-phase-search-log/record`: record that series were searched.
- `components/entity/sales-phase/get-by-series`: the existing per-series read of stored phases, which the new series selection calls; it has no spec yet.

### Modified Capabilities

- `components/entity/sales-phase` (Purpose and requirements): attribute table reduced; method required and the only classification; apply end time required for a lottery.
- `components/entity/sales-phase/search-sales-phases`: not-yet-opened sales only, required fields, no channel or provider classification, a failure always fails, timeline check reduced to the remaining milestones.
- `components/entity/sales-phase/upsert`: identity is series, method and apply start date in Japan time; the omitted-url scenario is gone.
- `components/entity/sales-phase/list-phases-with-pending-milestones`: the payment deadline sentence goes away with the attribute.
- `components/entity/sales-phase-reminder` (Purpose and requirements): three stages, anchored by method.
- `components/entity/ticket-journey/list-user-ids-tracking-series`: each tracking fan is returned with the event to link them to.
- `components/usecase/sales-phase/discover-for-artist`: series selection and the 30-day interval replace the 90-day window and the daily search of every series.
- `components/usecase/sales-phase/announce-discovered-phase`: specific copy and a per-recipient link.
- `components/usecase/sales-phase/scan-due-reminders`: stages by method, simpler quiet hours, new copy, per-recipient link.
- `components/usecase/sales-phase-reminder/deliver-reminder`: only the scenario that names the removed `APPLY_CLOSE_1H` stage changes; the behavior is unchanged.
- `stories/hear-about-a-new-ticket-sale` and `stories/get-reminded-of-ticket-sale-milestones`: the push titles, the milestones reminded and the quiet-hours rule follow the above.

These are unchanged: TicketJourney (other operations), the SalesPhaseReminder operations (AlreadySent, ListSentStages, RecordSent store stage values without interpreting them), Concert.ListEventsBySeries, and the organizer LotterySalesPhase, which shares only the name.

## Impact

- specification: `proto/liverty_music/entity/v1/sales_phase.proto` (**BREAKING**: `SalesChannel` and fields 5, 6, 7, 11 and 12 are removed and reserved; `method` becomes required). The message is used by no RPC, so no API client changes.
- backend:
  - `internal/infrastructure/gcp/gemini/sales_phase_searcher.go` (rewrite)
  - `internal/usecase` (sales_phase_uc, sales_reminder_uc, sales_phase_announcement_uc, sales_phase_link)
  - `internal/entity` (SalesPhase, ReminderStage, SalesPhaseSearchLog)
  - `internal/infrastructure/database/rdb` (sales_phase_repo, ticket_journey_repo, new search log repo)
  - one Atlas migration (dropped columns, new table)
  - `pkg/config` (model defaults; the window setting is removed)
- cloud-provisioning: the sales-phase-discovery ConfigMap (model `gemini-3.8-flash`, thinking `low`). The suspend patch on `sales-phase-discovery-app` is removed after rollout.
- The evaluation harness on backend branch `test/sales-phase-search-eval` carries the fixtures (King Gnu, tuki., Mrs. GREEN APPLE). It is test-only.
