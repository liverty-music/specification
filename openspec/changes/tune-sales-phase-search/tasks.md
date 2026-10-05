## 1. Proto (specification)

- [ ] 1.1 In `entity/v1/sales_phase.proto`, delete `SalesChannel` and fields 5, 6, 7, 11 and 12, reserving their numbers and names. Make `method` required with `not_in: [0]`, and add the CEL rule from design D8. Verify `buf lint`, `buf format -d` and `buf build` pass, and open the PR with the `buf skip breaking` label.
- [ ] 1.2 Merge, cut the GitHub Release, and verify the `buf-release.yml` run and BSR generation succeed.

## 2. Sales Phase entity and storage (backend; components/entity/sales-phase, components/entity/sales-phase/upsert, components/entity/sales-phase/get-by-series, components/entity/sales-phase/list-phases-with-pending-milestones)

- [ ] 2.1 Generate an Atlas migration per design D7: delete all reminder and phase rows, drop the five columns and their checks, add the method, lottery and close checks, the `apply_start_date_jst` generated column and the unique key. Update `schema.sql` to match and add the migration to the kustomization. Verify `atlas migrate lint` and `atlas migrate apply --env local` pass.
- [ ] 2.2 Remove `Channel`, `ProviderName`, `Sequence`, `PaymentDeadlineTime`, `URL`, `SourceURL` and `SalesChannel` from `entity.SalesPhase` and `SalesPhaseCandidate`. Add the validation for the entity rules and an application-ended check (`HasApplicationEnded(now)`). Verify unit tests annotated `@spec` pass for:
  - "Fan-club lottery", "No method"
  - "Lottery before its close", the two "First-come sale until sold out" scenarios
  - "Lottery without a close", "No start time", "Close before open", "Result before close", "Result on a first-come sale"
- [ ] 2.3 Rewrite `SalesPhaseRepository.Upsert` as the single `ON CONFLICT` statement from D7. Verify contract tests against local PostgreSQL pass for "Re-discovery with a corrected time", "Re-discovery with more detail", "Different start dates stay separate", "Different methods on one day stay separate", "Omitted value clears the stored one", and the unchanged Skipped and series-error scenarios.
- [ ] 2.4 Order `GetBySeries` by apply start time and validate a missing series. Verify contract tests pass for "Series with two phases", "Series with no phase" and "No series given".
- [ ] 2.5 Drop the payment deadline from `ListPhasesWithPendingMilestones`. Verify its existing contract tests still pass.

## 3. Search log (backend; components/entity/sales-phase-search-log and its operations)

- [ ] 3.1 Add `entity.SalesPhaseSearchLog` with the future-time check. Verify a unit test for "Future searched time" passes.
- [ ] 3.2 Add the `sales_phase_search_logs` table (D6) to the migration from 2.1, and implement `ListBySeries` and `Record` in `rdb`. Verify contract tests pass for "One searched, one never searched", "No series given", "Series searched again", "Series searched for the first time" and "Unknown series".

## 4. Tracking fans with their linked event (backend; components/entity/ticket-journey/list-user-ids-tracking-series)

- [ ] 4.1 Change `ListUserIDsTrackingSeries` to return each fan with their linked event (D10 query). Verify contract tests pass for "Fans tracking events of the series", "Linked event is the earliest upcoming tracked event", "Every tracked event is past" and the three unchanged exclusion scenarios.

## 5. Searcher (backend; components/entity/sales-phase/search-sales-phases)

- [ ] 5.1 Rewrite `SalesPhaseSearcher` as the single JSON call (D1, D2): delete the XML parser, Step 2, `sanitizeTimeline` and the parse config. Verify a unit test asserts the built request: tools and time range, the `ToolConfig` flag, MIME type, schema with the series enum, no temperature, and the prompt with the event period.
- [ ] 5.2 Implement the D3 checks over canned JSON responses. Verify unit tests pass for:
  - "Two rounds announced ahead", "Sale already open", "Sale abroad", "Year omitted"
  - "Lottery with a published result date", "Lottery without a published result date", "First-come sale until sold out", "Lottery without a stated close", "Method not stated", "Nothing usable found"
  - "Close before open", "Opening after the last show", "Unattributable sale", "No series given"
- [ ] 5.3 Implement the D4 failure mapping with a single attempt, and log `search_queries` from the tool-call parts. Verify unit tests pass for "Spend cap reached", "No result" and "Service unreachable", plus one asserting the logged queries.
- [ ] 5.4 Move the evaluation harness from `test/sales-phase-search-eval` in as a `GEMINI_SP_EVAL`-gated integration test against the production searcher. Verify `go vet -tags=integration ./internal/infrastructure/gcp/gemini/` passes, and one run on the fixtures finds at least 13 of 15 sales with 0 wrong values. That run covers "Artist with two tours" and "Official ticket trade".

## 6. Discovery usecase (backend; components/usecase/sales-phase/discover-for-artist)

- [ ] 6.1 Implement the D5 selection and the search log recording in `DiscoverForArtist`. Remove `GCP_SALES_PHASE_DISCOVERY_WINDOW` and `SalesPhaseWindow()`, and wire the new repository in `di/sales_phase_discovery_job.go`. Verify unit tests with mocked operations pass for:
  - "Tracked series with nothing pending", "Nobody tracks the series", "A phase is still open", "First-come sale until sold out has opened", "Searched recently", "Events far ahead", "Two tracked series", "No official site"
  - "Search finds nothing", "Search fails"
  - the unchanged store and announce scenarios
- [ ] 6.2 Set the searcher defaults in `pkg/config` (model `gemini-3.8-flash`, thinking `low`) and remove the parse and temperature settings from the sales-phase wiring. Verify the `pkg/config` tests and `go build ./...` pass.

## 7. Notifications (backend; components/entity/sales-phase-reminder, components/usecase/sales-phase/scan-due-reminders, components/usecase/sales-phase/announce-discovered-phase, components/usecase/sales-phase-reminder/deliver-reminder)

- [ ] 7.1 Delete `ReminderStageApplyClose1H` and make `scheduledFireTime` branch on method (D9). Verify unit tests pass for:
  - "Lottery stages", "First-come stage", "Lottery without a result time", "Undefined stage"
  - "First-come sale about to open", "First-come sale already open", "Lottery opens", "Already sent", "Result day", "Milestone already past when the phase was discovered", "Application window closed before the open reminder was sent", "Result day has ended"
  - "First-come sale at midnight", "Lottery opening during the night", "Close reminder at night", "Time zone fallback"
  - "Scan cadence", "Phase opening in 3 days", "One phase fails"
- [ ] 7.2 Replace the reminder copy, the time formatting and the link (D10), deleting `channelDisplayName` and `ResolveSeriesLinkURL`. Verify unit tests pass for "Lottery closing in Japanese", "Deferred close reminder keeps the absolute deadline", "Link to the tracked event", "Tracking fan" and "Fan no longer listed".
- [ ] 7.3 Replace the announcement copy and link (D10). Verify unit tests pass for "First-come sale in Japanese", "Lottery in English" and "Two fans tracking different shows", plus the unchanged audience, immediacy and request scenarios.
- [ ] 7.4 Update the DeliverReminder test fixture to `APPLY_CLOSE_24H`. Verify the "Reminder requested" and "Empty request" tests pass.
- [ ] 7.5 Open the backend PR citing this change and the store commit. Verify CI including `make lint` is green, then merge and cut a release.

## 8. Rollout (cloud-provisioning)

- [ ] 8.1 Update the sales-phase-discovery ConfigMaps per the Migration Plan (3.8 flash, thinking `low`, parse keys removed). Verify `kubectl kustomize` on the dev and prod overlays renders them.
- [ ] 8.2 Bump the prod image pin and remove `sales-phase-discovery-app` from the suspend patches. Verify `kubectl kustomize` shows the CronJob without `suspend: true` in both overlays, and that ArgoCD is Synced on the merge commit.
- [ ] 8.3 After the first 21:00 JST run, verify in Cloud Logging that the job completes without errors and that any search response carries `search_queries`. Also check that the billing export's search-query count for that hour matches the logged queries.

## 9. Stories (stories/hear-about-a-new-ticket-sale, stories/get-reminded-of-ticket-sale-milestones)

- [ ] 9.1 Update the story tests for the new copy, milestones and link. Verify they pass for:
  - "Tracking fan hears about the new phase", "Tapping the push", "Follower who tracks nothing", "Fan who has already applied" (both stories)
  - "First-come sale about to open", "Lottery reminders", "Lottery opening at 02:00", "First-come sale at midnight"
  - the unchanged once-only scenarios
