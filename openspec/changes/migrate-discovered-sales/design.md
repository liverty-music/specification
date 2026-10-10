## Context

See proposal.md - Why. This change builds on the `TicketSale` model of `unify-ticket-sales` (its design D1-D6) and on `FirstCome` from `first-come-ticket-sales`. `unify-ticket-sales` design "Non-Goals" leaves this move to a later change and shapes `TicketSale` so that "a Series-level sale with a method, a window and no ticket types" fits it.

Current state, verified 2026-10-10 on backend `main` (d53780d) and specification `main`:

- **Tables** (`backend/internal/infrastructure/database/rdb/schema/schema.sql`):
  - `sales_phases` (394-408): `method SMALLINT` with `1=LOTTERY, 2=FIRST_COME` (404, 414), nullable `apply_end_at` and `lottery_result_at`, `discovered_at DEFAULT NOW()`, and a generated `apply_start_date_jst`. CHECKs: result only on a lottery (405), a lottery has an end (406), end after start (407). The convergence key is `uq_sales_phases_series_method_start_date UNIQUE (series_id, method, apply_start_date_jst)` (408).
  - `sales_phase_search_logs` (424-427): one row per series.
  - `sales_phase_reminders` (436-445): `UNIQUE (user_id, sales_phase_id, stage)` (442). `stage` values are 1, 2 and 4, and 3 is unused (451).
  - `notifications.type` includes `sales_phase_announcement` (380).
  - `series.organizer_id` is NULL exactly for a discovery-pipeline series (139, 150-151, 161).
- **Code**:
  - `internal/entity/sales_phase.go`: `SalesMethod` mirrors the proto values. `ReminderStage`. `SalesPhase.HasApplicationEnded`. `SalesPhaseCandidate.Validate`. `SalesPhaseRepository`.
  - `sales_phase_search_log.go`.
  - Usecases `sales_phase_uc.go` (discovery), `sales_phase_announcement_uc.go`, `sales_reminder_uc.go` (scan) and `sales_reminder_delivery_uc.go`.
  - Repos `rdb/sales_phase_repo.go`, `sales_phase_reminder_repo.go`, `sales_phase_search_log_repo.go`, and the searcher `gcp/gemini/sales_phase_searcher.go`.
  - Event consumers `adapter/event/sales_phase_consumer.go` and `sales_reminder_consumer.go`, the jobs `di/sales_phase_discovery_job.go` and `di/sales_reminders_job.go`, and `cmd/job/sales-reminders`.
- **Identifiers keyed by the phase id**: the announcement's 2-minute de-duplication id is built from the phase id (`sales_phase_announcement_uc.go:109`). The reminder's device grouping tag is `sales-phase-<id>-stage-<n>` (`sales_reminder_uc.go:367`).
- **Discovery does not skip an Organizer's Series.** `selectSeriesToSearch` (`sales_phase_uc.go:206-230`) has no Organizer check. `Concert.ListByArtist` returns published first-party concerts with their `organizer_id` (`rdb/concert_repo.go:125-130`). The only represented-artist skip is in the concert search (`specs/components/usecase/concert/search-new-concerts/spec.md:21-23`). The brief's premise that discovery already excludes represented artists holds only for the concert search.
- **No RPC or screen exposes a discovered sale.**
  - `entity/v1/sales_phase.proto` is imported by no RPC proto (grep over `proto/`).
  - The backend never references `entityv1.SalesPhase` or `entityv1.SalesMethod`.
  - The frontend's only "sales phase" hits are the organizer lottery editor (`LotterySalesPhase`).
  - The fan sees discovered sales only as push notifications and the Notification records behind them.
- **Infrastructure names**:
  - NATS stream `SALES_PHASE` with subjects `SALES_PHASE.discovered` and `SALES_PHASE.reminder_due` (`internal/entity/event_data.go:30-35`, `internal/infrastructure/messaging/streams.go:91`, `cloud-provisioning/k8s/namespaces/nats/base/jetstream/stream-sales-phase.yaml`).
  - The CronJob `sales-phase-discovery`.
  - The log-based metric `sales_reminder_delivery_outcomes` (`cloud-provisioning/src/gcp/components/monitoring.ts:793-804`).
- **`TicketSale` after the two earlier changes**: `name` is required, 1-100 (unify D2). `end time` is required, and Lottery runs 1-14 days (unify D3). `TicketSale ||--|{ TicketType`. `ListDueForDraw` returns every undrawn Lottery sale past its end (unify `entity/ticket-sale/list-due-for-draw`). `TicketSaleMethod` gets Lottery and FirstCome. Its numbers are set by unify task 2.1 and are not yet fixed (the current proto has `FIRST_COME = 1`).

## Goals / Non-Goals

**Goals:**
- One sale entity. A discovered sale is a `TicketSale` with no `TicketType`, and all existing discovered data is kept with its ids.
- The discovered rules stay exactly as they are. Discovered data that is valid today stays valid.
- The reminder pipeline runs for the Organizer's sales too (proposal, decision 4) without a second code path.

**Non-Goals:**
- Announcing an Organizer's sale when it is created. Only discovered sales are announced, as today (Assumptions to confirm).
- Showing discovered sales on any fan screen.
- Renaming the infrastructure names: the NATS stream and subjects, the CronJob, the job binary and the log-based metric. They carry no domain meaning that a reader acts on, and renaming the stream means recreating it in `cloud-provisioning`. This can be a follow-up cleanup.
- Extracting a sale name from the official pages.

## Decisions

### D1 — The parent Series tells an Organizer's sale from a discovered one. No new field.

`components/entity/ticket-sale` "An Organizer's sale or a discovered sale" defines both from the Series' Organizer. Each kind has invariants that make it checkable within the sale:

| | Organizer's sale | discovered sale |
|---|---|---|
| Series | has an Organizer | no Organizer |
| TicketTypes | at least one | none |
| discovered time | absent | present |
| name | required | absent |
| verification requirement | any | None |

- **Why no `source` field:** every row in the table already follows from the Series. A field would be one more value that could disagree with `series.organizer_id`.
- **The database proxy is `discovered_at IS NOT NULL`.** A CHECK or a partial index cannot read `series.organizer_id`. `discovered_at` is an existing attribute with its own job, the first-sight guard of the reminder scan (`sales_phases.discovered_at` comment, schema.sql:418). It is present exactly on discovered rows, because only `UpsertDiscovered` sets it.
- **Who keeps the invariant:**
  - `TicketSale.Create` (Organizer) never sets `discovered_at`. `TicketSaleUseCase.Create` already requires TicketTypes and the caller's Series (unify `usecase/ticket-sale/create`).
  - `TicketSale.UpsertDiscovered` refuses a Series with an Organizer (FailedPrecondition) and never writes TicketTypes.
  - `TicketSaleDiscoveryUseCase.DiscoverForArtist` no longer searches an Organizer's Series. This closes the gap found in Context.
- **Rejected: the presence of TicketTypes as the only marker.** It is right in the entity but cannot drive a partial unique index either.

### D2 — Discovered rows fit `ticket_sales`

Columns added by one Atlas migration:

| column | type | rule |
|---|---|---|
| `lottery_result_at` | `TIMESTAMPTZ NULL` | only when `discovered_at IS NOT NULL` and method = Lottery; `>= end_at` |
| `discovered_at` | `TIMESTAMPTZ NULL` | set once by `UpsertDiscovered` and never updated |
| `start_date_jst` | `DATE GENERATED ALWAYS AS ((start_at AT TIME ZONE 'Asia/Tokyo')::date) STORED` | convergence key part |

Constraint changes:
- `name` becomes nullable, with `CHECK (discovered_at IS NOT NULL OR name IS NOT NULL)` and `CHECK (discovered_at IS NULL OR name IS NULL)`.
- `end_at` becomes nullable, with `CHECK (end_at IS NOT NULL OR (discovered_at IS NOT NULL AND method = FirstCome))`.
- The window-length CHECK of unify, if one exists, gets `discovered_at IS NOT NULL OR ...`.
- `CHECK (discovered_at IS NULL OR (verification_requirement = None AND drawn_at IS NULL))`.
- `uq_ticket_sales_discovered_convergence UNIQUE (series_id, method, start_date_jst) WHERE discovered_at IS NOT NULL` replaces `uq_sales_phases_series_method_start_date`.
  - **Why partial:** an Organizer may run two Lottery sales of one Series that open on the same day for different events. Unify D4 only forbids overlap per event. The discovery key must not forbid that.
  - The upsert uses `ON CONFLICT (series_id, method, start_date_jst) WHERE discovered_at IS NOT NULL DO UPDATE`. This keeps today's single-statement convergence (`rdb/sales_phase_repo.go:103`).

### D3 — The rules unify put on every sale apply to an Organizer's sale

`components/entity/ticket-sale` "A lottery window lasts 1 to 14 days", "A sale has a name" and "Required times depend on the method and the kind of sale" scope these rules to an Organizer's sale: the 1-to-14-day lottery window, the required name and the required end time for FirstCome. They are rules for selling on the platform. The 1-14 days come from the card hold and the draw, and the end time from checkout. None of them applies to a sale the platform only reports. `first-come-ticket-sales`' rule that the end comes no later than the event's start time is on the Organizer's FirstCome sale and its TicketTypes, so it is untouched.

In Go, `TicketSale.Validate` takes the kind (derived from `discovered_at` / the Series) and checks the matching rule set. `SalesPhaseCandidate.Validate` (`sales_phase.go`) becomes the discovered branch.

### D4 — The result time of a lottery

`components/entity/ticket-sale` "Result time of a lottery":
- **Discovered Lottery sale:** the stored `lottery_result_at`, as today.
- **Organizer's Lottery sale:** the end time. Its draw runs within 1 minute after it (`DrawDueSales`, unify D6), and `GetResult` answers from then on.
- An Organizer's sale never stores a lottery result time. A stored value later than the draw would contradict what `GetResult` shows.
- `RESULT_DAY` is anchored on the calendar day of the result time (`entity/ticket-sale-reminder`). For an Organizer's lottery it is due at 09:00 on the closing day, with the text "本日{end}に抽選結果発表!!".
- **Rejected: a reminder after the draw** ("results are out"). It needs a new anchor (the drawn time), a new copy row and a scan over drawn sales. Assumptions to confirm.

### D5 — Reminders for the Organizer's sales reuse the scan

- `TicketSale.ListWithPendingMilestones` returns both kinds, each with its TicketTypes. It returns an Organizer's sale only while its Series is `PUBLISHED`, so a cancelled Series is never reminded.
- The milestones are `start_at`, `end_at` and the result time. The result time is `COALESCE(lottery_result_at, CASE WHEN discovered_at IS NULL AND method = Lottery THEN end_at END)`.
- **Audience:**
  - Discovered sale: `TicketJourney.ListUserIDsTrackingSeries`, unchanged.
  - Organizer's sale: the new `TicketJourney.ListUserIDsTrackingEvents` over the events of its TicketTypes. A sale can offer only some events of a tour (unify D1), and a fan tracking only the Osaka show must not be told that a Tokyo-only lottery opened.
  - **Rejected: series-wide audience for both,** the literal reading of decision 4. It sends reminders for sales the fan cannot enter.
  - `ListUserIDsTrackingEvents` is the same query as `ListUserIDsTrackingSeries` with `event_id = ANY($1)` instead of a series join.
- **First-sight guard:** it applies only when `discovered_at` is set. An Organizer's sale created after it opened still gets `APPLY_OPEN`, whose text says the lottery is open and when it closes. The stage still expires at the end time.
- **The same copy is used for both kinds** (`entity/ticket-sale/scan-due-reminders` content table). Showing an Organizer's sale name in the text is a possible follow-up.
- **Notification ids stay stable.** The device tag becomes `ticket-sale-<id>-stage-<n>`. The announcement de-duplication id keeps its formula on the sale id. Ids are preserved (D7), so a reminder in flight across the deploy still de-duplicates by its record in `ticket_sale_reminders`.

### D6 — Names

| From | To |
|---|---|
| `SalesPhase`, `SalesPhaseCandidate` | `TicketSale` (discovered), `DiscoveredTicketSale` (search result) |
| `SalesMethod` (proto and Go) | `TicketSaleMethod` |
| `SalesPhaseRepository.Upsert / GetBySeries / ListPhasesWithPendingMilestones` | `TicketSaleRepository.UpsertDiscovered / ListBySeries / ListWithPendingMilestones` |
| `SalesPhaseSearcher.Search…` | `TicketSaleSearcher.SearchPublishedSales` |
| `SalesPhaseReminder(Repository)` | `TicketSaleReminder(Repository)` |
| `SalesPhaseSearchLog(Repository)` | `TicketSaleSearchLog(Repository)` |
| `SalesPhaseDiscoveryUseCase` | `TicketSaleDiscoveryUseCase` |
| `SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase` | `TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale` |
| `SalesReminderUseCase` | `TicketSaleReminderUseCase` |
| `SalesReminderDeliveryUseCase` | `TicketSaleReminderDeliveryUseCase` |
| notification type `sales_phase_announcement` | `ticket_sale_announcement` |
| tables `sales_phase_reminders`, `sales_phase_search_logs` | `ticket_sale_reminders`, `ticket_sale_search_logs` |

- `GetBySeries` → `ListBySeries`: it returns a list, as the other list operations do.
- The searcher operation is named for what it reads, the sales published on the official pages. `Search` alone would read as a store query on `TicketSale`.
- `ReminderStage` keeps its values 1, 2 and 4. Only the table's CHECK name changes.
- The notification type is renamed so that the stored vocabulary matches the specs. PostHog counts `notification.delivered` by type (`monitoring.ts:780`). With no users, the history break is accepted.

### D7 — Proto

- Delete `entity/v1/sales_phase.proto` (`SalesPhase`, `SalesPhaseId`, `SalesMethod`). Nothing imports it (Context). This is breaking on BSR and goes in with the `buf skip breaking` label.
- `ticket_sale.proto` keeps its fields. Its doc comment says that the message carries an Organizer's sale, that a discovered sale is not exposed over RPC, and why `name` and `end_time` stay required there.
- **Rejected: adding `lottery_result_time` and `discovered_time` to `TicketSale`.** No RPC reads them, and the review criteria allow a timestamp field only when a spec requirement reads it over the contract.

### D8 — Specs are replaced, not moved

The subject changes (phase → sale, and reminders now cover the Organizer's sales), so the old capabilities are REMOVED and the new ones ADDED at `entity/ticket-sale/*`, `entity/ticket-sale-reminder/*`, `entity/ticket-sale-search-log/*`, `usecase/ticket-sale/*` and `usecase/ticket-sale-reminder/*`, following unify D12. Each REMOVED requirement names where its behavior continues. Two old scenarios are corrected on the way:
- `sales-phase-reminder/already-sent` "Recorded" used the undefined stage `APPLY_CLOSE_1H`. The new spec uses `APPLY_CLOSE_24H`.
- `discover-for-artist` had two scenarios named "Search fails". The second is now "Search fails with a spend cap".

### D9 — Sequencing

1. `unify-ticket-sales` and `first-come-ticket-sales` archive first. The MODIFIED deltas on `entity/ticket-sale`, `entity/ticket-sale/list-due-for-draw` and `usecase/notification/deliver` copy their text. `openspec validate` already reports that archive would refuse those two deltas until `entity/ticket-sale` exists on main.
2. When they archive, task 0.1 re-copies each MODIFIED block from the then-current main spec. `first-come-ticket-sales` rewrites its deltas onto unify's model (unify task 8.1), so "Purchase notification requested" in `notification/deliver` may change from "buyer" to "user".
3. `concert/delete-and-suppress` and `user/delete` also mention the lottery sales phase and ticket applications that unify removes, and unify has no delta for them. This change writes their post-unify wording ("TicketTypes … with their lottery entries", "lottery entries"). If unify adds its own deltas first, this change keeps only the TicketSale and reminder parts (task 0.1). `organizer/delete` ("each Event's lottery sales phases, ticket applications", spec.md:13) has the same gap. That one is unify's to fix and is reported, not changed here.

## Risks / Trade-offs

- [Real discovered data moves] → Task 0.2 reads counts and samples read-only first. The migration keeps every id, so reminder records and the announcement de-duplication still match. A migration test loads every CHECK branch: a lottery with and without a result time, and a first-come sale without an end.
- [Method numbers differ: `SalesMethod` 1/2 vs `TicketSaleMethod`] → The migration maps by name with an explicit `CASE`, never by casting. The migration test asserts the mapping.
- [Turning reminders on for the Organizer's sales at deploy] → A sale already open but not past its end gets `APPLY_OPEN` on the first scan. Only test sales exist, so this is accepted.
- [Organizer's lottery: two pushes on the closing day] (`APPLY_CLOSE_24H` at 08:00 when the end is late evening, and `RESULT_DAY` at 09:00) → They say different things. Assumptions to confirm.
- [Organizer sale invariants are kept by the application, not the database] (D1) → Only two writers exist (`Create`, `UpsertDiscovered`), each with a contract test for the refusal.
- [The draw job could pick up discovered lotteries] → `ListDueForDraw` adds `discovered_at IS NULL`, covered by the scenario "Discovered lottery has closed". Without it, the draw would set `drawn_at` on every discovered lottery and break the CHECK.

## Migration Plan

1. Specification PR: delete `sales_phase.proto` and add the `ticket_sale.proto` doc comment. Release, then BSR gen.
2. Backend PR with one Atlas migration, in one transaction:
   1. Alter `ticket_sales` as in D2.
   2. `INSERT INTO ticket_sales (id, series_id, name, method, start_at, end_at, lottery_result_at, discovered_at, verification_requirement, drawn_at) SELECT id, series_id, NULL, CASE method WHEN 1 THEN <Lottery> WHEN 2 THEN <FirstCome> END, apply_start_at, apply_end_at, lottery_result_at, discovered_at, <None>, NULL FROM sales_phases`.
   3. `ALTER TABLE sales_phase_reminders RENAME TO ticket_sale_reminders`, rename `sales_phase_id` → `ticket_sale_id`, and repoint its foreign key to `ticket_sales(id) ON DELETE CASCADE`. The ids match, so no row changes.
   4. `ALTER TABLE sales_phase_search_logs RENAME TO ticket_sale_search_logs`.
   5. `UPDATE notifications SET type = 'ticket_sale_announcement' WHERE type = 'sales_phase_announcement'`.
   6. `DROP TABLE sales_phases`.
3. Deploy the backend: discovery job, reminder job and consumers together. No frontend PR.
4. Verify in production, read-only (task 6.x):
   - row counts equal task 0.2;
   - `AtlasMigration` is applied;
   - the next 21:00 discovery run and the 15-minute scan log no errors;
   - a reminder for a migrated discovered sale is not sent twice.
5. Rollback: the migration is forward-only. Before step 2, task 0.2 takes a Cloud SQL on-demand backup. If the deploy fails, fix forward, or restore that backup (or point-in-time recovery to before the migration) and redeploy the previous backend image. Discovered data written after the migration is lost on restore, and the next daily run finds it again.

## Assumptions to confirm

1. **A discovered sale has no name** (gap a). The search does not extract one, and no screen shows a discovered sale. Alternative: store a default such as 抽選 / 先着, which is Japanese text in every locale and claims a name the page did not give.
2. **An Organizer's lottery's result time is its end time** (gap b). `RESULT_DAY` arrives at 09:00 on the closing day, and an Organizer's sale cannot store a lottery result time. Alternative: a "results are out" reminder after the draw (D4).
3. **Discovered windows have no length limit, and a discovered FirstCome sale may have no end** (gap c). The Organizer-only rules are scoped by kind (D3).
4. **The convergence key is a partial unique index on discovered rows** (gap d). An Organizer's sales are not constrained by it (D2).
5. **The audience of an Organizer's sale is the fans tracking an event it offers,** not every fan tracking the Series (D5). This narrows decision 4 for sales that cover only some events of a tour.
6. **An Organizer's sale is not announced when it is created.** Only reminders are added (decision 4).
7. **A fan who entered an Organizer's lottery still gets `APPLY_CLOSE_24H`** unless their ticket journey is Applied. An entry does not set the journey (unify `usecase/lottery-entry/enter`). Skipping entrants needs a lookup of the sale's entries per scan.
8. **The infrastructure names stay** (Non-Goals). The notification type value is renamed.
9. **An Organizer's sale is reminded only while its Series is Published.** A Cancelled Series stops its reminders.
