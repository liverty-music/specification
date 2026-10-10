## 0. Dependency gate and production pre-check

- [ ] 0.1 Confirm `unify-ticket-sales` and `first-come-ticket-sales` are archived. Then re-copy every MODIFIED block of this change from the main specs as they stand (design D9): `entity/ticket-sale` ("A lottery window lasts 1 to 14 days", "A sale has a name"), `entity/ticket-sale/list-due-for-draw`, `usecase/notification/deliver`, `entity/user/delete` and `entity/concert/delete-and-suppress`. Keep every existing scenario name. Verify `openspec validate migrate-discovered-sales --strict` passes with no "Archive would refuse this delta" notice
- [ ] 0.2 Through the db-proxy runbook (read-only), read the row counts of `sales_phases` (per method, with and without `apply_end_at` and `lottery_result_at`), `sales_phase_reminders` (per stage), `sales_phase_search_logs` and `notifications` of type `sales_phase_announcement`. Also count `sales_phases` rows whose series has an `organizer_id`, which must be 0 (design D1). Record the numbers in design.md "Migration Plan", and take a Cloud SQL on-demand backup before the migration. Verify the numbers are recorded and the backup is listed by `gcloud sql backups list --configuration=liverty-music`. If a row's series has an Organizer, stop and ask the user

## 1. Specification: main spec Purposes and plan PR

- [ ] 1.1 Edit the main spec Purposes directly (design D8). Verify `openspec validate --specs` and `python3 scripts/check-spec-layout.py` pass:
  - `components/entity/ticket-sale`:
    - discovered sales in the first sentence, with the two kinds named;
    - `name` optional (absent on a discovered sale);
    - `end time` optional for a discovered FirstCome sale;
    - new rows `lottery result time` (discovered Lottery only, not before the end time) and `discovered time` (discovered sales only, set once);
    - method `Lottery` or `FirstCome`;
    - erDiagram `TicketSale ||--o{ TicketType` and `TicketSale ||--o{ TicketSaleReminder`.
  - `components/entity/series`: erDiagram `Series ||--o{ TicketSale : "sells through"`.
  - `components/entity/notification`: type `ticket_sale_announcement`, and "a ticket sale announcement" in the first sentence.
  - `components/entity/ticket-journey/list-user-ids-tracking-series`: "ticket sales phases" → "discovered ticket sales".
  - `stories/hear-about-a-new-ticket-sale`: "a new ticket sales phase" → "a new discovered ticket sale".
- [ ] 1.2 Open the plan PR from a worktree cut from origin/main (README "Branch work in this repository"). Stage only `openspec/changes/migrate-discovered-sales` and the main specs edited in 1.1. Verify `openspec-checks.yml` passes and the PR merges

## 2. Proto (specification → BSR)

- [ ] 2.1 Delete `proto/liverty_music/entity/v1/sales_phase.proto`. In `ticket_sale.proto`, add a doc comment to `TicketSale` saying that the message carries an Organizer's sale, that a discovered sale is never returned over RPC, and why `name` and `end_time` stay required (design D7). Verify `buf lint` and `buf format -d` pass and `grep -rn "SalesPhase\b\|SalesMethod" proto` finds nothing
- [ ] 2.2 Open the proto PR from a worktree with the `buf skip breaking` label, merge, and cut a Release. Verify `buf-release.yml` succeeds and BSR has the new version

## 3. Backend: migration (design D2, "Migration Plan")

- [ ] 3.1 Write one Atlas migration:
  - alter `ticket_sales`: `lottery_result_at`, `discovered_at`, generated `start_date_jst`, nullable `name` and `end_at`, the kind-scoped CHECKs, and the partial unique index `uq_ticket_sales_discovered_convergence`;
  - copy every `sales_phases` row with its id, mapping the method with an explicit `CASE` by name;
  - rename `sales_phase_reminders` to `ticket_sale_reminders`, with `ticket_sale_id` and its foreign key repointed to `ticket_sales`;
  - rename `sales_phase_search_logs` to `ticket_sale_search_logs`;
  - rewrite `notifications.type`;
  - drop `sales_phases`;
  - update `schema.sql` and its comments.

  Verify the migration applies to a fresh database after every earlier migration, `make lint-schema` passes, and the prod Atlas overlay registers it
- [ ] 3.2 Add a migration test. Load the following, apply the migration and check every row:
  - a lottery with an end and a result time, a lottery without a result time, a first-come sale without an end and a first-come sale with an end;
  - two reminders (stages 1 and 4);
  - one search log;
  - one `sales_phase_announcement` notification;
  - one Organizer's lottery sale created by `unify-ticket-sales`.

  Verify the test passes: ids are unchanged, methods map by name, the reminders point at the same sale ids, the Organizer's sale is untouched, and a second discovered row with the same series, method and Japan date is refused while a second Organizer's sale of that series on that date is accepted

## 4. Backend: entities and entity operations

- [ ] 4.1 `TicketSale` kinds and rules (`components/entity/ticket-sale`, design D1, D3, D4). Fold `SalesPhaseCandidate.Validate` into the discovered branch of `TicketSale` validation, and remove `entity/sales_phase.go`'s `SalesPhase` and `SalesMethod` in favour of `TicketSale` and `TicketSaleMethod`. Verify one unit test per scenario: Lottery window within bounds, Lottery window shorter than 1 day, Lottery window longer than 14 days, End not after start, Discovered lottery longer than 14 days, Named sale, Empty name, Discovered sale without a name, Organizer's presale, Sale found by discovery, Discovered sale with a TicketType, Organizer's sale without a TicketType, First-come sale until sold out, Lottery without a close, Organizer's first-come sale without a close, Result before close, Result on a first-come sale, Result time on an Organizer's lottery, Discovered lottery with an announced result, Organizer's lottery, Discovered lottery without an announced result, Re-discovery keeps the discovered time, Lottery before its close, First-come sale until sold out has opened
- [ ] 4.2 `TicketSaleReminder` and `TicketSaleSearchLog` (`components/entity/ticket-sale-reminder`, `components/entity/ticket-sale-search-log`), renamed from the sales phase types. `ReminderStage` keeps 1, 2 and 4, and the anchors use the sale's result time. Verify one unit test per scenario: Undefined stage, Lottery stages, First-come stage, Lottery without a result time, Organizer's lottery, Future searched time
- [ ] 4.3 `TicketSaleRepository.UpsertDiscovered`, `ListBySeries` and `ListWithPendingMilestones` (design D2, D5). `ListWithPendingMilestones` returns TicketTypes, computes the result time, and keeps an Organizer's sale only while its Series is `PUBLISHED`. Verify one contract test per scenario against Postgres:
  - upsert-discovered: Unknown start, Sale no longer discovered, No series, Unknown series, Series of an Organizer, Lottery without a close, Re-discovery with a corrected time, Re-discovery with more detail, Different start dates stay separate, Different methods on one day stay separate, Omitted value clears the stored one
  - list-by-series: Series with two sales, Series with no sale, No series given
  - list-with-pending-milestones: Opened weeks ago, result tomorrow, Opens beyond the lookahead, All milestones long past, Latest milestone just past, Organizer's sale opening tomorrow, Organizer's sale of a cancelled Series, Nothing pending, Zero lookahead, Negative lookback
- [ ] 4.4 `TicketSale.ListDueForDraw` excludes discovered sales (`discovered_at IS NULL`). Verify the contract tests Closed and undrawn, Still open, Already drawn and Discovered lottery has closed pass
- [ ] 4.5 `TicketSaleReminderRepository.AlreadySent / ListSentStages / RecordSent` and `TicketSaleSearchLogRepository.ListBySeries / Record` on the renamed tables. Verify one contract test per scenario: Recorded, Not recorded, Missing ticket sale (AlreadySent), Some stages sent, No users given, Missing ticket sale (ListSentStages), First record, Repeated record, Missing user, One searched, one never searched, No series given, Series searched again, Series searched for the first time, Unknown series
- [ ] 4.6 `TicketJourney.ListUserIDsTrackingEvents` (`components/entity/ticket-journey/list-user-ids-tracking-events`), the same query as `ListUserIDsTrackingSeries` filtered by event ids. Verify one contract test per scenario: Fans tracking offered events, Linked event is among the given events, Tracking only an event not given, A fan past the Tracking stage, No event given
- [ ] 4.7 Rename the Gemini searcher to `TicketSaleSearcher.SearchPublishedSales`, returning discovered sales (`components/entity/ticket-sale/search-published-sales`); the prompt and response schema keep their content. Verify the unit tests pass for Artist with two tours, Unattributable sale, No series given, Close before open, Opening after the last show, Spend cap reached, No result, Service unreachable, Invalid request recovered without the tool report, Invalid request rejected twice. Then run the existing evaluation integration test (`sales_phase_eval_integration_test.go`, renamed) once against real pages and verify its pass rate is not lower than on `main`, covering Two rounds announced ahead, Sale already open, Official ticket trade, Sale abroad, Year omitted, and the five "Required values come from the source pages" scenarios

## 5. Backend: usecases, consumers and jobs

- [ ] 5.1 `TicketSaleDiscoveryUseCase.DiscoverForArtist` (`components/usecase/ticket-sale/discover-for-artist`), which skips a Series with an Organizer (design D1). Verify unit tests with the operations mocked: Daily run, One sale cannot be stored, Search fails, New sale, Known sale discovered again, Announcement request fails, Tracked series with nothing pending, Organizer's series, Nobody tracks the series, A sale is still open, First-come sale until sold out has opened, Searched recently, Ten days counted by date, Nine days counted by date, Events far ahead, Two tracked series, No official site, Search finds nothing, Search fails with a spend cap
- [ ] 5.2 `TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale` (`components/usecase/ticket-sale/announce-discovered-sale`) with the notification type `ticket_sale_announcement`, and `NotificationUseCase.Deliver`'s caller list (`components/usecase/notification/deliver`). Verify unit tests: New discovered sale created, Request without a series, Organizer's sale created, Tracking fan, Nobody tracking, Profile unreadable, Late evening, Two recipients, Request fails, Same sale announced twice, First-come sale in Japanese, Lottery in English, Two fans tracking different shows, Notification requested, Purchase notification requested, Recording fails for one request, Discovered sale announced
- [ ] 5.3 `TicketSaleReminderUseCase.ScanDueReminders` (`components/usecase/ticket-sale/scan-due-reminders`). It covers both kinds, uses the audience per kind and the first-sight guard only for discovered sales, and tags `ticket-sale-<id>-stage-<n>` (design D5). Verify unit tests: Scan cadence, Sale opening in 3 days, Organizer's sale is evaluated, One sale fails, Tracking fan, Organizer's sale for some events of the tour, Fan no longer listed, Reminder requested, First-come sale about to open, First-come sale already open, Lottery opens, Already sent, Result day, Organizer's lottery result day, Milestone already past when the sale was discovered, Organizer's sale created after it opened, Application window closed before the open reminder was sent, Result day has ended, First-come sale at midnight, Lottery opening during the night, Close reminder at night, Time zone fallback, Lottery closing in Japanese, Deferred close reminder keeps the absolute deadline, Link to the tracked event
- [ ] 5.4 `TicketSaleReminderDeliveryUseCase.DeliverReminder` (`components/usecase/ticket-sale-reminder/deliver-reminder`). Verify unit tests: Reminder requested, Empty request, Repeated request, Check fails, Delivered to a device, Accepted by a device, No device, Push fails, Recording fails after delivery
- [ ] 5.5 Rewire the event consumers, the discovery and reminder jobs and the DI graph to the renamed usecases. The NATS subjects, the CronJob name and the log line `sales_reminder delivery outcome` stay (design Non-Goals). Rename `entity/notification.go`'s type constant. Verify `make check` passes and `grep -rn "SalesPhase" internal cmd` finds no type or function name
- [ ] 5.6 `User.Delete` and `Concert.DeleteAndSuppress` (modified specs) on the renamed tables. Verify the contract tests Existing user, Purchases outlive the user, Unknown id, Empty id, Reminder records go with the user, Concert with fan journeys and Series stays pass
- [ ] 5.7 Rewrite the story tests (`rdb/sales_phase_story_test.go` → a ticket sale story test) for `stories/get-reminded-of-ticket-sale-milestones` and `stories/hear-about-a-new-ticket-sale`, running the scan, delivery and announcement against Postgres with a fake push channel. Verify each scenario passes: Next scan, No registered browser (both stories), First-come sale about to open, Lottery reminders, Fan who has applied, Lottery opening at 02:00, First-come sale at midnight, Organizer's lottery reminders, Organizer's first-come sale, Sale for another event of the tour, Series cancelled before the sale opens, Tracking fan hears about the new phase, Tapping the push, Follower who tracks nothing, Fan who has already applied, Same phase found the next day
- [ ] 5.8 Upgrade the generated package to the 2.2 release, run `make check`, open the backend PR citing the change, and merge. Verify the AtlasMigration status is applied in production and the backend, event-consumer and job rollouts are healthy

## 6. Production verification (read-only)

- [ ] 6.1 Read the migrated rows through the db-proxy runbook. Verify the counts of discovered `ticket_sales` (per method, with and without an end and a result time), `ticket_sale_reminders` (per stage), `ticket_sale_search_logs` and `ticket_sale_announcement` notifications equal task 0.2, and that no `sales_phase*` table remains
- [ ] 6.2 After the first 21:00 Japan-time discovery run and an hour of reminder scans following the deploy, read the job and consumer logs (`gcloud logging read --configuration=liverty-music`). Verify the discovery job finished without an error, the scan logged no error, and no `sales_reminder` notification was created after the deploy for a user, sale and stage already in `ticket_sale_reminders` before it (compare `ticket_sale_reminders.sent_at` with the notification's tag `ticket-sale-<id>-stage-<n>`)
