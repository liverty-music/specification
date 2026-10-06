## Context

See proposal.md - Why. Sales-phase discovery runs as the `sales-phase-discovery` CronJob (daily 21:00 JST, prod and dev currently suspended). It calls `usecase.SalesPhaseDiscoveryUseCase.DiscoverForArtist` once per followed artist. The job's circuit breaker stops the run after 3 consecutive artist failures. Today the searcher (`internal/infrastructure/gcp/gemini/sales_phase_searcher.go`) makes two Gemini calls:

1. gemini-3.6-flash with Google Search and URL context, returning an XML envelope.
2. gemini-3.1-flash-lite with a JSON schema, coercing dates.

Retries are exhausted into "no phases". Announcements are built in `sales_phase_announcement_uc.go`. Reminders are built in `sales_reminder_uc.go` (scan) and delivered by `sales_reminder_delivery_uc.go`. Both resolve a series-wide link through `ResolveSeriesLinkURL`. No RPC or screen exposes SalesPhase; the proto message is used only as the schema source.

Evaluation (2026-10-05, test-only harness `TestSalesPhaseSearchEval` on backend branch `test/sales-phase-search-eval`; current time frozen at 2026-10-05T15:00+09:00; fixtures checked against official pages):

| configuration (gemini-3.8-flash, thinking low, 30-day search window) | search queries / call | sales found | wrong values |
|---|---|---|---|
| schema with url, channel, provider name, payment deadline; event dates listed | 25.9 | 13 / 15 | 0 (3 of 3 tuki. urls were invented 404 pages) |
| url and payment deadline removed; event period instead of dates; "every later round" rule | 14.4 | 14 / 15 | 0 |
| channel and provider name also removed (final) | 10.2 | 13 / 15 | 0 |

Fixtures:

- King Gnu "KICKOFF": two fan-club lotteries taken by ローチケ.
- tuki.: two series, one e+ official first-come presale.
- Mrs. GREEN APPLE "SHADOWS": two fan-club first-come sales without an end.

Every miss was the second sale of a series; the final schedule rule searches the series again once the first sale has ended (D5). For comparison, the 2026-09 prod run averaged 13.5 queries per call and was 58% accurate.

## Goals / Non-Goals

**Goals:**
- Ship the evaluated searcher configuration and the simplified Sales Phase.
- Spend search queries only on tracked series, at most once per 30 days per series unless a known sale has ended.
- Make every failure visible and retried by the next daily run.
- Reminder and announcement copy that is correct after quiet-hours shifts and names the tour.

**Non-Goals:**
- Showing sales phases on the concert page or in any RPC (follow-up).
- Changing the concert searcher (change `tune-concert-search-grounding`).
- Fixing stale artist official-site URLs (in progress in change `refresh-artist-official-site`).
- Verifying the line break rendering on an iOS device (no task, by decision).

## Decisions

**D1. Searcher request.**

- Model `gemini-3.8-flash`, thinking `low`, temperature not sent.
- Tools: `GoogleSearch` with `TimeRangeFilter` from now minus 30 days to now (truncated to whole seconds), and `URLContext`.
- `ToolConfig.IncludeServerSideToolInvocations = true`, so the search queries are logged per call from the tool-call parts.
- One call with `ResponseMIMEType: application/json` and `ResponseJsonSchema`.
- The Step 2 call, the XML envelope and its parser, `sanitizeTimeline` and the flash-lite model setting are deleted.
- `SalesPhaseConfig` keeps `APIKey`, `Model` and `Thinking`. `ModelParse`, `ThinkingParse` and `Temperature` are removed.

Alternative: keep the two-step pipeline. It needed one more call and two parsers, and in evaluation the single call had no value errors.

**D2. Prompt and schema (as evaluated).**

System instruction:

```
You extract ticket sales for concerts from official web pages, for a service that tells fans about upcoming sales.

Task: for each series in the user prompt, find the ticket sales whose application period has not started at the current time.

A sale is one application period under one method: for example a fan-club lottery, a playguide presale, or a general on-sale. Include lotteries and first-come sales, presales and general on-sales, and every later round of a series (2次, 3次, ...) that has not started yet. Do not include ticket trades or resales between ticket holders.

Sources: the artist's official site, official tour pages, and ticketing-service pages for the series. Do not use any other site.

Return a sale only if a source page states every required field. If any required field is missing, leave the sale out. Never infer or guess a value.

Return JSON that follows the response schema. Return an empty phases array if no sale qualifies.
```

User prompt: `Current time: <RFC 3339>`, `Artist:`, `Official site: <full URL>`, then per series `- id:`, `title:`, `event_period: <first> to <last>` (upcoming events only).

Schema: `phases[]`, every item with these keys, all required:

- `series_id`: an enum of the given ids
- `method`: `lottery` | `first_come`
- `apply_start_time`: string
- `apply_end_time`: string | null; required for a lottery, null only for a first-come sale that ends when tickets run out
- `lottery_result_time`: string | null; null if not stated or first come

The time fields share one description: RFC 3339 with the UTC offset of the time zone the page uses, with examples for Japan and Taipei. A year omitted on the page is taken as the one that places the date before the end of the event period.

Naming follows the gemini package's existing `start_time` / `open_time` and AIP `_time`, not the `_at` database columns.

**D3. Application-side checks** (deterministic, after parsing; a failed check drops the sale and is logged with its reason):

- `series_id` is one of the given series.
- `method` is `lottery` or `first_come`.
- `apply_start_time` parses and is after now.
- A lottery has `apply_end_time`.
- `apply_end_time` is after `apply_start_time`.
- `lottery_result_time` is not before `apply_end_time`, and appears only on a lottery.
- `apply_start_time` is not after the end of the last day of the series' event period, in Japan time.

A year mistake into the past is removed by "after now", and one into the future by the last check.

**D4. Failure mapping.** One attempt per search (no backoff loop). Errors map as follows:

| cause | error |
|---|---|
| Transport error or 5xx | Unavailable |
| 429, including the AI Studio spend cap | ResourceExhausted |
| 4xx | the matching apperr code |
| Context deadline | DeadlineExceeded |
| Empty candidates, a non-STOP finish reason, or invalid JSON (including a truncated response) | Internal |

The usecase returns the error. The job then counts the artist as failed, and its existing 3-consecutive-errors breaker stops the run, which is the intended behavior when the spend cap is hit. A failed search records no search log (D5), so the next daily run retries. No in-call retry, because a failed grounded call is still billed.

**D5. Series selection** in `DiscoverForArtist`, in this order, cheapest first:

1. Group `Concert.ListByArtist(upcoming)` into series, with their first and last upcoming dates.
2. Keep the series for which `TicketJourney.ListUserIDsTrackingSeries` is not empty.
3. Drop a series when `SalesPhase.GetBySeries` has a phase whose application has not ended. A phase ends at its apply end time, or at its apply start time for a first-come sale without one.
4. Drop a series when `SalesPhaseSearchLog.ListBySeries` shows a searched time within the last 30 days.
5. If any series is left, read the official site and call the searcher once.

Afterwards, upsert each phase and announce the inserted ones, then `Record` all searched series at the search start time. The 30 days is a constant in the usecase. `GCP_SALES_PHASE_DISCOVERY_WINDOW` and `SalesPhaseWindow()` are deleted.

Alternative: a per-artist interval. It was simpler storage, but a newly tracked series of a recently searched artist would wait up to 30 days.

**D6. Search log storage.** New table `app.sales_phase_search_logs`:

- `series_id UUID PRIMARY KEY REFERENCES series(id) ON DELETE CASCADE`
- `searched_at TIMESTAMPTZ NOT NULL`

`Record` is one `INSERT … ON CONFLICT (series_id) DO UPDATE` over `unnest($1::uuid[])`. A foreign-key violation maps to FailedPrecondition. `ListBySeries` is `WHERE series_id = ANY($1)`. The interface `entity.SalesPhaseSearchLogRepository` goes in `internal/entity/sales_phase_search_log.go`, and the implementation in `rdb/sales_phase_search_log_repo.go`.

Alternative: a column on `series`. It was rejected because it mixes a discovery concern into the shared Series entity.

**D7. Sales Phase storage.** One migration:

- `DELETE FROM sales_phase_reminders;` and `DELETE FROM sales_phases;`. Both are 0 and 130 rows in prod. No reminder was ever sent.
- Drop the columns `channel`, `provider_name`, `sequence`, `payment_deadline_at` and `url`, and their check constraints.
- `method` gets `CHECK (method IN (1, 2))`.
- Add `CHECK (method = 1 OR lottery_result_at IS NULL)`, `CHECK (method = 2 OR apply_end_at IS NOT NULL)` and `CHECK (apply_end_at IS NULL OR apply_end_at > apply_start_at)`.

Upsert key: `UNIQUE (series_id, method, apply_start_date_jst)`, where `apply_start_date_jst` is a stored generated column `DATE GENERATED ALWAYS AS ((apply_start_at AT TIME ZONE 'Asia/Tokyo')::date) STORED`. Upsert is `INSERT … ON CONFLICT (series_id, method, apply_start_date_jst) DO UPDATE SET apply_start_at, apply_end_at, lottery_result_at RETURNING id, (xmax = 0) AS inserted`. This replaces the application-side match on series and exact apply start time; the table has no unique key today.

The Go `entity.SalesPhase` and `SalesPhaseCandidate` lose `Channel`, `ProviderName`, `Sequence`, `PaymentDeadlineTime`, `URL` and `SourceURL`. The `SalesChannel` type is deleted.

**D8. Proto.** In `entity/v1/sales_phase.proto`:

- Delete `enum SalesChannel`.
- Remove fields 5 (channel), 6 (provider_name), 7 (sequence), 11 (payment_deadline_time) and 12 (url), adding them to `reserved` by number and name.
- `method` becomes `REQUIRED` with `(buf.validate.field).enum = {defined_only: true, not_in: [0]}`.
- Add a message-level CEL rule: `this.method == SALES_METHOD_LOTTERY ? has(this.apply_end_time) : !has(this.lottery_result_time)`.

The PR carries the `buf skip breaking` label. No RPC references the message.

**D9. Reminder stages.**

- `entity.ReminderStage` keeps `APPLY_OPEN = 1`, `APPLY_CLOSE_24H = 2` and `RESULT_DAY = 4`. `APPLY_CLOSE_1H = 3` is deleted, and its value is left unused. The sent-log check stays `stage BETWEEN 1 AND 10`.
- `scheduledFireTime(stage, phase, tz)` branches on `phase.Method`:
  - `FIRST_COME` `APPLY_OPEN`: base is start minus 30 minutes and expiry is start. If base is in quiet hours, fire at 21:00 on the local date of the quiet window's start: the same day when base is at or after 22:00, the previous day when base is before 08:00.
  - `LOTTERY` `APPLY_OPEN` and `APPLY_CLOSE_24H`: in quiet hours, fire at the next 08:00. Because the close anchor is 24 hours before the end, the next 08:00 is always earlier than the end.
  - `RESULT_DAY`: unchanged.

  `preQuietAlertTime` for close stages is removed.

**D10. Copy and links.**

- `buildReminderPayload` and the announcement builder take `(phase, stage, user, seriesTitle, linkEventID)`, with the tables from the specs as `map[lang]map[key]string`.
- Time format, with the weekday from a fixed table:
  - ja: `1/2(月) 15:04`
  - en: `Jan 2 (Mon) 15:04`
- Text is `<sentence>\n<series title>`. The service worker passes `body` to `showNotification` unchanged.
- `TicketJourney.ListUserIDsTrackingSeries` returns `[]entity.SeriesTracker{UserID, EventID}`. The SQL picks, per user, the tracked event `ORDER BY (local_event_date < current_date), local_event_date LIMIT 1` with `DISTINCT ON (user_id)`.
- The link is `/concerts/<EventID>`. The frontend route `concerts/:id` already opens that event's detail sheet. `ResolveSeriesLinkURL` and the dashboard fallback are deleted, because a tracker always has a tracked event.
- The series title is read once per phase (`Series.Get`).
- `channelDisplayName` is deleted.

## Risks / Trade-offs

- [Search counts vary per call (4–27 observed)] → per-call `search_queries` logging; the AI Studio monthly spend cap stays the hard stop, and the job breaker stops a capped run after 3 artists.
- [The second sale of a series is sometimes missed] → it is found by the search after the first sale ends (D5). A first-come sale opening within 30 days of a recorded search and before the earlier sale ends is missed; this cadence gap is accepted.
- [A first-come sale discovered less than 30 minutes before it opens gets no reminder (first-sight guard)] → discovery runs at 21:00; accepted.
- [Two sales of the same series and method opening on the same Japan date collapse into one phase] → copy does not distinguish them; accepted.
- [Structured output with built-in tools and `include_server_side_tool_invocations` are Preview features] → a rejection surfaces as InvalidArgument in the job failures; rollback by the prod image pin.
- [Deleting stored phases loses nothing visible] → no screen or RPC reads them and no reminder was sent; still-upcoming sales are re-discovered.
- [The line break may render differently on iOS] → Chrome on Android shows it as a space when collapsed and as a line break when expanded (verified in Chromium's notification builder); iOS is accepted untested by decision.

## Manual verification

@spec-manual components/usecase/sales-phase/scan-due-reminders "Scan cadence" -- the sales-reminders CronJob in cloud-provisioning runs on schedule "*/15 * * * *" (k8s/namespaces/backend/base/cronjob/sales-reminders/cronjob.yaml); checked with kubectl kustomize.

## Migration Plan

1. specification PR: this change plus the proto edit (`buf skip breaking`). Merge, release, wait for BSR gen.
2. backend PR: migration (D6, D7), entity, repositories, searcher, usecases, copy, config, tests including the `@spec` annotations. Rebase the evaluation harness into `internal/infrastructure/gcp/gemini/sales_phase_eval_integration_test.go` as a gated integration test. Then release.
3. cloud-provisioning PR:
   - sales-phase-discovery ConfigMap (base and prod): `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.8-flash` and `GCP_GEMINI_SEARCH_THINKING_EXTRACT=low`. Remove `GCP_GEMINI_SEARCH_MODEL_PARSE` and `GCP_GEMINI_SEARCH_THINKING_PARSE`.
   - Bump the prod image pin.
   - Remove `sales-phase-discovery-app` from the prod and dev suspend patches. Delete the patch file when concert-discovery has already been resumed by `tune-concert-search-grounding`, otherwise narrow its target.
4. After ArgoCD sync, the first 21:00 run logs `sales_phase_discovery` skips, and searches only tracked series (none today, so zero queries).

Rollback: revert the image pin and ConfigMap, and re-suspend the CronJob. The migration is forward-only; the deleted phases had no consumer.
