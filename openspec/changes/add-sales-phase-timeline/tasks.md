## 0. Prerequisites

- [ ] 0.1 `auto-discovery-series-grouping` is implemented/merged so a `Series` represents a whole tour (the Series-scoped `SalesPhase` model depends on it)
- [ ] 0.2 At OpenSpec archive time, ensure the in-flight `ticket-email-import` change is archived first (this change MODIFIES its spec baseline)

## 1. Proto Definitions (specification)

- [ ] 1.1 Define `SalesPhaseId` wrapper message (UUID) in `entity/v1/sales_phase.proto`
- [ ] 1.2 Define `SalesMethod` enum (`UNSPECIFIED`, `LOTTERY`, `FIRST_COME`) in `entity/v1/sales_phase.proto`
- [ ] 1.3 Define `SalesChannel` enum (`UNSPECIFIED`, `FAN_CLUB`, `OFFICIAL`, `PLAYGUIDE`, `CREDIT_CARD`, `MOBILE_CARRIER`, `GENERAL`)
- [ ] 1.4 Define `SalesPhase` message: `id`, `series_id` (required), `repeated EventId event_ids` (covered events), `method`, `channel`, `provider_name`, `sequence`, nullable `apply_start_time`/`apply_end_time`/`lottery_result_time`/`payment_deadline_time`, nullable `url` (reuse `Url` VO); use `_time` naming, no `_at`
- [ ] 1.5 (Optional) Add a reference RPC / compose `repeated SalesPhase` on the concert-detail response if surfacing on concert detail this phase
- [ ] 1.6 Run `buf lint` and `buf format -w`; verify no breaking changes (additive only; `ticket_email.proto` untouched)
- [ ] 1.7 Open specification PR; after review + CI, merge and publish a GitHub Release to trigger BSR gen (CI-only; do not run `buf push`/`buf generate` locally)

## 2. Database Migration (backend)

- [ ] 2.1 Create Atlas migration for `sales_phases` table (id UUID PK, series_id FK→series, method SMALLINT, channel SMALLINT, provider_name TEXT, sequence INT, apply_start_at/apply_end_at/lottery_result_at/payment_deadline_at TIMESTAMPTZ nullable, url TEXT nullable)
- [ ] 2.2 Enforce uniqueness on the derived phase identity (stable + collision-free; must NOT collapse two UNSPECIFIED-channel/default-sequence phases — disambiguate via apply_start_at, else provider_name, else extraction order)
- [ ] 2.3 Create `event_sales_phases` join table (`sales_phase_id`, `event_id`) for the covered-events M:N relationship; each `event_id` references an event of the phase's series
- [ ] 2.4 Create `sales_phase_reminders` sent-log table with unique `(user_id, sales_phase_id, stage)` (reference the phase surrogate id, not series_id+sequence)
- [ ] 2.5 Apply migration locally and verify with `atlas migrate apply --env local`; confirm `ticket_emails` is unchanged

## 3. Backend Entity & Repository

- [ ] 3.1 Define `SalesPhase` entity struct, `SalesMethod`/`SalesChannel` constants in `internal/entity/sales_phase.go`
- [ ] 3.2 Define `SalesPhaseRepository` interface (Upsert by stable logical identity, ListUpcomingByDueWindow, GetBySeries, replace covered `event_ids`)
- [ ] 3.3 Implement pgx-based `SalesPhaseRepository`: upsert via the collision-free stable identity (not raw `(series_id, channel, sequence)`), last-write-wins on timeline/url/provider_name, and replace the `event_sales_phases` rows for the phase
- [ ] 3.4 Add the actionable-data guard (skip persistence when no timestamp and no method+url)
- [ ] 3.5 Write repository integration tests (upsert idempotency, last-write-wins, guard)

## 4. Sales-Phase Searcher (backend)

- [ ] 4.1 Create `internal/infrastructure/gcp/gemini/sales_phase_searcher.go` modeled on the two-step concert searcher
- [ ] 4.2 Implement Step 1 grounded verbatim extraction (input: artist name + series title; retain source URL)
- [ ] 4.3 Implement Step 2 JSON coercion of dates/times only (no invented values)
- [ ] 4.4 Define the Japanese sales-schedule extraction prompt
- [ ] 4.5 Extract each phase's covered dates and resolve them to the series' known `event_id`s; drop unresolvable dates (no guessing)
- [ ] 4.6 Write unit tests with mock Gemini responses (verbatim → coerce → SalesPhase shaping; covered-event resolution; empty grounding → no phase)

## 5. Discovery Job (backend + cloud-provisioning)

- [ ] 5.1 Implement `internal/usecase/sales_phase_uc.go` discovery use case (enumerate followed artists' upcoming series → searcher → upsert)
- [ ] 5.2 Create `cmd/job/sales-phase-discovery/main.go` entrypoint following the `concert-discovery` pattern
- [ ] 5.3 Wire into DI graph (Google Wire)
- [ ] 5.4 On persisting a NEW phase, publish a `SALES_PHASE.discovered` event (skip re-announcement for already-known phases); add the subject constant
- [ ] 5.5 Add an announcement consumer in `internal/adapter/event/` that resolves the phase's covered events → performers → followers (hype filter) and pushes via `webpush.Sender`; wire into DI + router
- [ ] 5.6 Write use-case tests (idempotent re-run produces no duplicates; new phase announces once, re-discovery does not)
- [ ] 5.7 Add `cronjob/sales-phase-discovery/cronjob.yaml` (daily) in cloud-provisioning

## 6. Multi-Stage Reminders (backend + cloud-provisioning)

- [ ] 6.1 Implement `internal/usecase/sales_reminder_uc.go`: scan due phases, compute stages (open / 24h-before / 1h-before / result-day; NOT payment-deadline), resolve each phase's covered `event_ids`→performers→followers reusing the hype filter from `NotifyNewConcerts`
- [ ] 6.2 Publish a `SALES_PHASE.reminder.due` event; add the subject constant and a new consumer in `internal/adapter/event/`
- [ ] 6.3 Reminder consumer sends via existing `webpush.Sender` + `PushSubscriptionRepository.ListByUserIDs`; reuse gone-subscription cleanup
- [ ] 6.4 Enforce once-only delivery via the `sales_phase_reminders` sent-log
- [ ] 6.5 Create `cmd/job/sales-reminders/main.go` entrypoint (scan + publish)
- [ ] 6.6 Wire into DI graph; register the consumer handler
- [ ] 6.7 Write tests: correct stage selection, null milestone → no reminder, idempotent sent-log (no double send)
- [ ] 6.8 Add `cronjob/sales-reminders/cronjob.yaml` (~15-minute schedule) in cloud-provisioning
- [ ] 6.9 Confirm Vertex AI / DB access IAM for the two new jobs

## 7. Disable Email Import Entry (frontend)

- [ ] 7.1 Remove the `share_target` entry from `manifest.webmanifest`
- [ ] 7.2 Disable the Service Worker share-target POST interception handler
- [ ] 7.3 Make the `/import/ticket-email` route unavailable: remove its navigation entry and present an unavailable state on direct access (retain components + RPC client code)
- [ ] 7.4 Run `make check` (frontend)

## 8. Integration & Release

- [ ] 8.1 Backend: `go get` the released schema version, `go mod tidy`, swap placeholder types for generated `SalesPhase` types, run `make check`
- [ ] 8.2 Local verification: run `cmd/job/sales-phase-discovery` against a known series → SalesPhase persisted and visible on concert detail
- [ ] 8.3 Local verification: run `cmd/job/sales-reminders` against a near-deadline phase → exactly one push per stage (sent-log idempotency)
- [ ] 8.4 Open backend, frontend, and cloud-provisioning PRs only after package upgrade + type swap pass locally
- [ ] 8.5 After merges, verify ArgoCD rollout and the new CronJobs are scheduled
