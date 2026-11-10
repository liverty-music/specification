## 1. backend: shared contracts and layer direction

- [ ] 1.1 Move the event message contract (payload decoding, `ce_subject`, the redelivery mark and its reader) from `internal/infrastructure/messaging` into a new `pkg/` package. Switch `internal/adapter/event` and `internal/infrastructure/messaging` to it. Verify that `go test ./internal/adapter/event/... ./internal/infrastructure/messaging/... ./pkg/...` passes, including the redelivery tests.
- [ ] 1.2 Move the caller context contract (`Claims`, the caller Organization id, their context setters and getters) from `internal/infrastructure/auth` into a new `pkg/` package. The interceptors stay in `infrastructure/auth`. Switch the adapters (`rpc`, `pb`, `webhook`) to it. Verify that the auth interceptor tests and the handler tests pass.
- [ ] 1.3 Declare the webhook token check as an interface in `internal/adapter/webhook`, and inject `auth.WebhookValidator` through it in `internal/di`. Verify that the `pre_access_token_handler` tests pass with a mockery mock of the interface.
- [ ] 1.4 Move `PrefectureName` and the Series image variant object key into `internal/entity`, and switch `adapter/linkpreview`, `adapter/pb`, `infrastructure/geo` and `infrastructure/gcp/storage` to them. Verify that the moved unit tests pass in `internal/entity`.
- [ ] 1.5 Create `internal/entitypb` holding the entity-to-`entity/v1` mapping that announcements use, the `ForAnnouncement` variants included. Switch the 21 infrastructure files and `adapter/pb` to it, and update backend `AGENTS.md` "Announcements" to name it. Verify that `go test ./internal/infrastructure/database/rdb/...` passes, including every announcement test.
- [ ] 1.6 Enable depguard in `.golangci.yml` with the layer rules of design.md, and verify that `make lint` reports no depguard finding.
- [ ] 1.7 Switch the `follow`, `concert`, `push_subscription`, `notification`, `wallet_public_key` and `ticket_journey` handlers from `entity.UserRepository` to `usecase.UserUseCase` (`callerUserID` / `ResolveCaller`), and update their wiring in `internal/di`. Verify that each handler's tests pass with the UserUseCase mock, including the NotFound case for a caller without a stored User.

## 2. backend: errors and the clock

- [ ] 2.1 Make every entity validator and guard return an `apperr` error with the code its callers attach today: InvalidArgument for the validators, FailedPrecondition for `ValidateLotteryEntrySale` and the state guards. Rewrite the comments at `user.go:35`, `user.go:70` and `settlement.go:136` to state the rule. Verify with entity tests that assert the code of each rule's failure.
- [ ] 2.2 Make the callers in `internal/usecase` and `internal/infrastructure/database/rdb` return those errors as they are. Replace the nine `apperr.New(code, err.Error())` sites listed in design.md with `apperr.Wrap`, or with a plain return where the entity now carries the code. Verify that usecase tests assert the same codes as before, and that `grep -rn 'apperr.New(.*err.Error()' internal` finds nothing.
- [ ] 2.3 Pass the time into `NewIdentityVerification` and `DiscoveredTicketSale.Validate`. Verify that `grep -n 'time.Now' internal/entity/*.go` finds no non-test hit, and that their tests use a fixed time.
- [ ] 2.4 Make every usecase that calls `time.Now()` read the injected `Clock` (workflows read it inside a step). Verify that `grep -n 'time.Now()' internal/usecase/*.go` finds only the `Clock` default, and that the affected tests pin the time.

## 3. backend: rules on entities

Before replacing the duplicates of a rule, diff them. Report any behavioural difference to the user before merging, and let the stating spec decide.

- [ ] 3.1 Add the 本人確認 gate (a sale's requirement against the fan's IdentityVerification, and "any sale of the event requires it") to the entity. Use it from `lottery_entry_uc`, `checkout_uc`, `resale_entry_uc` and `order_resale_workflow`. Verify with an entity table test (no verification, inactive, active; requirement None, Verified-any, JPKI-only), and with one usecase case per authorize-card / start spec scenario.
- [ ] 3.2 Add the required-purchaser-details validator and use it in the three usecases. Verify with an entity table test and the existing usecase scenarios.
- [ ] 3.3 Add the active-Organizer guard and use it at the six `organizer_uc.go` sites. Verify with an entity test per status, and with the deactivated-Organizer scenarios of the organizer usecase specs.
- [ ] 3.4 Move the unresold-Ticket refund amount (`order_refund_uc.go` `unresoldAmount`) and the Settlement split invariants (`settlement_uc.go` `buildSplits`) onto Order and Settlement. Verify with entity table tests covering the `usecase/order/refund` "Fan refunded the full amount" scenarios (one resold, every Ticket resold) and the split constraints of `entity/settlement`.
- [ ] 3.5 Move publish readiness (`series_uc.go` `validatePublishReadiness`) onto Series, and replace `eventVenueName` with `Concert.VenueName`. Verify with an entity table test for each `usecase/series/publish` failure (blank title, no performer, an Event without Venue or date).
- [ ] 3.6 Move the deletion-blocker classification of `user_uc.go` `ListDeletionBlockers` into one predicate per record kind on the entities. Verify with entity table tests for the four kinds of `usecase/user/list-deletion-blockers`, and reduce the usecase test to the orchestration cases.
- [ ] 3.7 Move `checkEndBeforeEvents` and the sale-open checks (`openFirstComeSale`, the ended-lottery check) onto TicketSale. Verify with entity table tests per method (Lottery, FirstCome) and boundary instant.
- [ ] 3.8 Move `scheduledFireTime` and `ticketSaleSearchDue` next to `ReminderStage.Anchor` on the entity, and drop their `export_test.go` exports. Verify with entity table tests for the `usecase/ticket-sale/scan-due-reminders` quiet-hour scenarios.
- [ ] 3.9 Put one venue-date-start key and one matcher on Event, and use them from `concert_creation_uc`, `concert_candidate_uc`, `concert_uc` and `FilterNewSeries`. Verify with an entity table test for the `entity/event` same-performance rule (unknown start matches only unknown start) and the existing usecase tests.
- [ ] 3.10 Replace `sameVenue` and `sameInstant` in `series_uc.go` with Event methods, and verify with entity tests for both and the existing Series update usecase tests.
- [ ] 3.11 Use `Order.CanBecomeVoid`, `Event.CanTransitionTo`, `Checkout.CanBecome` and `ResaleEntry.IsWithdrawable` where design.md lists them, and delete any that still have no caller. Verify that `go test ./internal/...` passes, and that a grep shows each kept method has a production caller.
- [ ] 3.12 Replace the hand-written fakes in usecase tests with the mockery mocks (`make mocks`), and trim the usecase cases that only re-checked a moved rule to one per spec scenario. Verify that `go test ./internal/usecase/...` passes, and that `grep -nE '^type (fake|stub|spy|recording|memory)[A-Za-z]* struct' internal/usecase/*_test.go` finds nothing.

## 4. backend: fan visibility

- [ ] 4.1 State the visibility or DRAFT filtering in the doc comment of every SeriesRepository method (the ConcertRepository ones are task 3.1 of `fix-backend-contract-drift`) whose query uses `fanVisibilityGuard`, `fanVisibleCondition` or `catalogEventCondition`, and verify by review against the queries the method runs.
- [ ] 4.2 For each of those methods, add an rdb table test. Seed Events in every combination (discovered or first-party; DRAFT, PUBLISHED or CANCELLED; PUBLIC or UNLISTED), and assert that the method returns exactly the Events the entity predicate (`Event.IsPubliclyVisible`, or the catalog rule) accepts. Add the same check for `seriesPublishStateColumn` against `DerivePublishState`. Verify that the rdb suite passes.

## 5. backend: function size

- [ ] 5.1 Enable funlen (60 lines, 40 statements, comments ignored), gocognit (20) and cyclop (15) in `.golangci.yml`, with `_test.go` excluded.
- [ ] 5.2 Split every reported function in `internal/usecase` and `internal/entity` by responsibility, and verify that `make lint` reports none there and `go test ./internal/usecase/... ./internal/entity/...` passes.
- [ ] 5.3 Split every reported function in `internal/infrastructure` (rdb, gemini, music clients, pocketsign, auth, server), and verify that `make lint` reports none there and `go test ./internal/infrastructure/...` passes.
- [ ] 5.4 Split every reported function in `internal/adapter`, `internal/di`, `pkg/config` and `cmd/`, and verify that `make lint` reports none there and their tests pass.
- [ ] 5.5 Collect any function that cannot be split without hurting clarity, with the reason, and ask the user before adding a `//nolint`. Verify that `make check` passes with no funlen, gocognit or cyclop finding, and that every `//nolint` added is one the user agreed to.
