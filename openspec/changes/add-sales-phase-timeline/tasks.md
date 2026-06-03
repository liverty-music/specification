## 0. Prerequisites

- [ ] 0.1 `auto-discovery-series-grouping` is implemented/merged so a `Series` represents a whole tour (the Series-scoped `SalesPhase` model depends on it) — NOT met yet (that change is 0/21); code is built against the assumed tour-level Series and needs no migration once it lands
- [ ] 0.2 At OpenSpec archive time, ensure the in-flight `ticket-email-import` change is archived first (this change MODIFIES its spec baseline)

## 1. Proto Definitions (specification)

- [x] 1.1 Define `SalesPhaseId` wrapper message (UUID) in `entity/v1/sales_phase.proto`
- [x] 1.2 Define `SalesMethod` enum (`UNSPECIFIED`, `LOTTERY`, `FIRST_COME`) in `entity/v1/sales_phase.proto`
- [x] 1.3 Define `SalesChannel` enum (`UNSPECIFIED`, `FAN_CLUB`, `OFFICIAL`, `PLAYGUIDE`, `CREDIT_CARD`, `MOBILE_CARRIER`, `GENERAL`)
- [x] 1.4 Define `SalesPhase` message: `id`, `series_id` (required), `repeated EventId event_ids` (covered events), `method`, `channel`, `provider_name`, `sequence`, nullable `apply_start_time`/`apply_end_time`/`lottery_result_time`/`payment_deadline_time`, nullable `url` (reuse `Url` VO); use `_time` naming, no `_at`
- [ ] 1.5 (Optional) Add a reference RPC / compose `repeated SalesPhase` on the concert-detail response if surfacing on concert detail this phase — deferred (design Open Question: surfacing on concert detail is not decided for this phase)
- [x] 1.6 Run `buf lint` and `buf format -w`; verify no breaking changes (additive only; `ticket_email.proto` untouched)
- [ ] 1.7 Open specification PR; after review + CI, merge and publish a GitHub Release to trigger BSR gen (CI-only; do not run `buf push`/`buf generate` locally) — PR #578 opened and green/merge-ready; merge + Release pending (gated on user + prereq 0.1 coordination)

## 2. Database Migration (backend)

- [x] 2.1 Create Atlas migration for `sales_phases` table (id UUID PK, series_id FK→series, method SMALLINT, channel SMALLINT, provider_name TEXT, sequence INT, `apply_start_at TIMESTAMPTZ NOT NULL`, apply_end_at/lottery_result_at/payment_deadline_at TIMESTAMPTZ nullable, url TEXT nullable)
- [x] 2.2 Store an immutable `anchor_event_id` (set once at insert as a representative); the surrogate `id` is the only uniqueness constraint. Do NOT add a unique constraint over `(series_id, channel, sequence)`/anchor — convergence is the application-level best-effort overlap match (see repo task 3.3), so incremental coverage growth never re-keys a phase into a duplicate
- [x] 2.3 Create `event_sales_phases` join table (`sales_phase_id`, `event_id`) for the covered-events M:N relationship; each `event_id` references an event of the phase's series
- [x] 2.4 Create `sales_phase_reminders` sent-log table with unique `(user_id, sales_phase_id, stage)` (reference the phase surrogate id, not series_id+sequence)
- [ ] 2.5 Apply migration locally and verify with `atlas migrate apply --env local`; confirm `ticket_emails` is unchanged — BLOCKED: local Docker (Rancher WSL integration) unavailable. Migration SQL + `schema.sql` written and `atlas.sum` regenerated (`atlas migrate hash`); apply + verify pending docker

## 3. Backend Entity & Repository

- [x] 3.1 Define `SalesPhase` entity struct, `SalesMethod`/`SalesChannel` constants in `internal/entity/sales_phase.go` (enum values match the proto exactly)
- [x] 3.2 Define `SalesPhaseRepository` interface (best-effort upsert by covered-event overlap, `ListPhasesWithPendingMilestones` (renamed from `ListUpcomingByDueWindow` to load phases by any pending milestone, not just apply_start), GetBySeries, replace covered `event_ids`)
- [x] 3.3 Implement pgx-based `SalesPhaseRepository`: match a fresh phase to an existing row by `series_id` AND covered-event overlap (anchor_event_id stored once, never recomputed for matching); on match, last-write-wins on timestamps/url/provider_name and replace `event_sales_phases`; else insert. Incremental coverage growth updates in place, not duplicate. `Upsert` returns an insert/update/skip outcome to gate announce-once
- [x] 3.4 Add the persistence guard: skip a phase unless `apply_start_time` is known AND ≥1 covered event resolved (no start / no coverage → drop)
- [x] 3.5 Write repository integration tests (overlap match converges, incremental coverage growth → no duplicate, per-leg disjoint coverage → separate rows, last-write-wins, guard) — written; execution against a DB pending docker (2.5)

## 4. Sales-Phase Searcher (backend)

- [x] 4.1 Create `internal/infrastructure/gcp/gemini/sales_phase_searcher.go` modeled on the two-step concert searcher
- [x] 4.2 Implement Step 1 grounded verbatim extraction (input: artist name + series title; retain source URL)
- [x] 4.3 Implement Step 2 JSON coercion of dates/times only (no invented values)
- [x] 4.4 Define the Japanese sales-schedule extraction prompt
- [x] 4.5 Resolve coverage to events: inject the series' candidate events (index-tagged: event_id/date/venue/admin_area) into Step 2 via the existing `step2InputEvent`/`byIndex` mechanism; Step 2 returns covered indices per phase; map indices→`event_id`s; drop unresolvable dates (no guessing); set `anchor_event_id` = earliest covered
- [x] 4.6 Write unit tests with mock Gemini responses (verbatim → coerce → SalesPhase shaping; covered-event resolution; empty grounding → no phase)
- [x] 4.7 Add `sales_phase_searcher_integration_test.go` with `//go:build integration` (mirroring the existing `searcher_integration_test.go`) so a real Gemini call can be run manually via `go test -tags=integration` with credentials, exercising the prompt + extraction + coverage resolution against live data

## 5. Discovery Job (backend + cloud-provisioning)

- [x] 5.1 Implement `internal/usecase/sales_phase_uc.go` discovery use case (enumerate followed artists' upcoming series → searcher → upsert)
- [x] 5.2 Create `cmd/job/sales-phase-discovery/main.go` entrypoint following the `concert-discovery` pattern
- [x] 5.3 Wire into DI graph
- [x] 5.4 On persisting a NEW phase, publish a `SALES_PHASE.discovered` event (skip re-announcement for already-known phases; gated on the upsert insert/update outcome); add the subject constant
- [x] 5.5 Add an announcement consumer in `internal/adapter/event/` that resolves the phase's covered events → performers → followers (hype filter) and pushes via `webpush.Sender`; wire into DI + router
- [x] 5.6 Write use-case tests (idempotent re-run produces no duplicates; new phase announces once, re-discovery does not)
- [x] 5.7 Add `cronjob/sales-phase-discovery/cronjob.yaml` (daily) in cloud-provisioning

## 6. Multi-Stage Reminders (backend + cloud-provisioning)

- [x] 6.1 Implement `internal/usecase/sales_reminder_uc.go`: scan due phases, compute stages (open / 24h-before / 1h-before / result-day at 09:00 local; NOT payment-deadline), skip milestones already past at first sight, resolve each phase's covered `event_ids`→performers→followers reusing the hype filter (`ShouldNotify`) from `NotifyNewConcerts`
- [x] 6.1a Apply quiet hours (22:00–08:00 in `users.time_zone`, fallback `Asia/Tokyo`): non-deadline stages defer to 08:00; deadline stages defer to 08:00 only if before `apply_end_time`, else bring forward to prior 22:00 (never wake, never past deadline)
- [x] 6.1b Build notification content per recipient (reuse `NotificationPayload`): times in the recipient's timezone, copy by `preferred_language` (default en), generic ticket label when channel=UNSPECIFIED, `url`→phase.url else concert detail, `tag`=`(sales_phase_id, stage)`
- [x] 6.2 Publish a `SALES_PHASE.reminder.due` event; add the subject constant and a new consumer in `internal/adapter/event/`
- [x] 6.3 Reminder consumer sends via existing `webpush.Sender` + `PushSubscriptionRepository.ListByUserIDs`; reuse gone-subscription cleanup
- [x] 6.4 Enforce once-only delivery via the `sales_phase_reminders` sent-log
- [x] 6.5 Create `cmd/job/sales-reminders/main.go` entrypoint (scan + publish)
- [x] 6.6 Wire into DI graph; register the consumer handler
- [x] 6.7 Write tests: correct stage selection, null/past milestone → no reminder, quiet-hours shift (defer vs. bring-forward, never past deadline), per-recipient TZ/language content, idempotent sent-log (no double send)
- [x] 6.8 Add `cronjob/sales-reminders/cronjob.yaml` (~15-minute schedule) in cloud-provisioning
- [x] 6.9 Confirm Vertex AI / DB access IAM for the two new jobs — no new IAM required; both reuse KSA `backend-app`→GSA which already holds `roles/aiplatform.user` + `roles/cloudsql.instanceUser`

## 7. Disable Email Import Entry (frontend)

- [x] 7.1 Remove the `share_target` entry from `manifest.webmanifest`
- [x] 7.2 Disable the Service Worker share-target POST interception handler
- [x] 7.3 Make the `/import/ticket-email` route unavailable: remove its navigation entry and present an unavailable state on direct access (retain components + RPC client code)
- [x] 7.4 Run `make check` (frontend) — passes; committed and pushed (PR #417)

## 8. Integration & Release

- [ ] 8.1 Backend: `go get` the released schema version, `go mod tidy`, swap placeholder types for generated `SalesPhase` types, run `make check` — BLOCKED on BSR gen (needs spec PR merge + Release first); internal types carry `TODO: swap to generated type after BSR gen` markers
- [ ] 8.2 Local verification: run `cmd/job/sales-phase-discovery` against a known series → SalesPhase persisted and visible on concert detail — BLOCKED on docker + prereq 0.1
- [ ] 8.3 Local verification: run `cmd/job/sales-reminders` against a near-deadline phase → exactly one push per stage (sent-log idempotency) — BLOCKED on docker
- [ ] 8.4 Open backend, frontend, and cloud-provisioning PRs only after package upgrade + type swap pass locally — frontend PR #417 opened (independent, no type dependency); backend + cloud-provisioning PRs pending BSR gen + type swap
- [ ] 8.5 After merges, verify ArgoCD rollout and the new CronJobs are scheduled
