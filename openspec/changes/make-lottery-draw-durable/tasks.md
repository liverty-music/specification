## 1. Prerequisites

- [ ] 1.1 Confirm `remove-lottery-entry-withdrawal` is merged and released in backend (no Withdrawn state, `GetOrCreateDraft` in place); verify `git log origin/main` of backend shows its PR
- [ ] 1.2 Read-only in prod, list the database pool size of every workload from the prod config maps (`cloud-provisioning/k8s/namespaces/backend/overlays/prod/*/configmap.env`, defaults from `backend/pkg/config/config.go`) and Zitadel's, and record in design.md that adding 3 DBOS connections keeps the total within `max_connections=25`; if it does not, lower a pool in the same PR

## 2. DBOS runtime (backend infrastructure)

- [ ] 2.1 Add `github.com/dbos-inc/dbos-transact-golang` at v1.7.0; generate the `dbos` schema migration with `dbos migrate --print-migrations all` and the grants with `dbos migrate --print-user-role --app-role <fan IAM role>`, commit them as one Atlas migration, and limit `scripts/lint-schema.sh` to the `app` schema; verify `make lint-schema` passes and the migration applies to a local database
- [ ] 2.2 Declare `Flow`, `StepOption` and the `Step` helper in `internal/usecase/workflow.go`, and implement them in `internal/infrastructure/workflow/dbos.go` (own `pgxpool` of 3 connections through the Cloud SQL dialer, `SkipMigrations`, `DatabaseSchema: "dbos"`, `ApplicationVersion: "1"`, registration by stable name, `Launch` only when `RunsPaymentSweepers()`); verify an integration test against local Postgres runs a two-step workflow, stops the process between the steps, launches again and sees the first step not re-run
- [ ] 2.3 Carry the trace context: `Enqueue` writes `traceparent` / `tracestate` to the workflow attributes, a run starts a span from it and a child span per step, and a resumed run starts a new root span linked to it; verify a unit test of the attribute round trip and, in the integration test, that a step's span has the enqueuing span's trace id
- [ ] 2.4 Register the `payment` queue (partition per TicketSale, `WithPartitionConcurrency(5)`, rate limit 20 per second) and the `draw-due-sales` schedule (`* * * * *`, `AutomaticBackfill`); verify the integration test sees one `DrawDueSales` run per minute and two enqueues with one id run once
- [ ] 2.5 Document in `backend/AGENTS.md`: values that change between runs are read inside a step; a change to a registered workflow's steps uses `dbos.Patch`; the module upgrade adds the printed migrations first; verify the section exists in the PR

## 3. Entity operations (components/entity/lottery-entry/record-draw-outcome, revert-win, components/entity/ticket-sale/record-draw)

- [ ] 3.1 Declare and implement `LotteryEntry.RecordDrawOutcome`; verify one contract test per scenario passes ("Outcome recorded", "Recorded again", "Another outcome", "Failure leaves nothing recorded")
- [ ] 3.2 Declare and implement `LotteryEntry.RevertWin`; verify the contract tests "Win reverted", "Already reverted", "Win already issued", "Not drawn" pass
- [ ] 3.3 Declare and implement `TicketSale.RecordDraw`; verify the contract tests "Draw recorded", "Recorded again", "First-come sale" pass
- [ ] 3.4 Remove `LotteryEntry.PersistDrawOutcome` and `Order.ListLotteryEntryIDsAwaitingIssuance` with their tests and mocks; verify `make check` passes with no reference left

## 4. Usecases (components/usecase/lottery-entry/draw, draw-due-sales, components/usecase/order/issue, components/usecase/card-authorization/release, components/usecase/order/fulfill-payment)

- [ ] 4.1 Implement `LotteryEntryUseCase.Draw` as a workflow and remove `RunDraw`; verify one unit test per scenario passes with a fake `Flow` and mocked operations ("Winners and losers recorded", "Each ticket type is drawn against its own quantity", "Losers in draw order", "Unconfirmed draft at the draw", "No entries", "Stopped after one ticket type", "Two entries, one place"), and that each Won entry enqueues `issue:<entry>` and each Lost entry and Draft with a card authorization enqueues `release:<card authorization>`
- [ ] 4.2 Change `LotteryEntryUseCase.DrawDueSales` to enqueue `Draw(sale)` with the id `draw:<sale>`; verify the unit tests "Window closes", "Window still open", "Drawn once", "One sale fails" pass
- [ ] 4.3 Implement `OrderUseCase.Issue` for a LotteryEntry as a workflow (retry options of design "24-hour retries") and remove `IssueFromCapturedWin` and `IssueDueWins`; verify one unit test per scenario of "Every Won entry is issued", "Charge, then issue", "Identity verification binding", "The paid Order is announced" and "A paid order is reported for product analytics" passes
- [ ] 4.4 Implement `CardAuthorizationUseCase.Release` as a workflow; verify the unit tests "Loser released", "Unconfirmed draft released", "Payment provider unavailable", "Charged card authorization" pass
- [ ] 4.5 Change `OrderUseCase.FulfillPayment` to succeed without effect for a LotteryEntry; verify the unit tests of "Each completed charge ends in an announced Order" pass, including "Lottery win charged"
- [ ] 4.6 Remove the lottery draw and issuance goroutines from `internal/di/provider.go` and wire the workflows; verify `make check` passes and the local fan workload logs DBOS launched with the schedule

## 5. Story (stories/win-tickets-in-a-lottery)

- [ ] 5.1 Extend `lottery_story_integration_test.go` to run the lottery through the DBOS workflows against local Postgres and a fake payment provider; verify "Demand within quantity", "Oversubscribed sale", "Count changed before confirming", "Entry left unconfirmed" and the new "Stopped after the first charge" (stop the process after the first capture, launch again, assert the same winners, one charge each, 2 Issued Tickets each, the loser never charged) pass
- [ ] 5.2 Run `make test-stripe-e2e` with the Stripe Sandbox key and confirm the authorize and capture legs still pass

## 6. Release and production check

- [ ] 6.1 Read-only in prod before the deploy, list Lottery sales due for a draw and Won entries without an Order; record the counts in design.md and stop if a Won entry without an Order exists (design "Migration Plan")
- [ ] 6.2 Merge the backend PR, cut the release, and confirm in prod (read-only) that the AtlasMigration applied the `dbos` schema, the fan-api rollout finished, and `dbos.workflow_status` holds a `draw-due-sales` run for each minute since the rollout
- [ ] 6.3 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the run succeeds

## 7. Archive

- [ ] 7.1 Edit the main spec Purposes this change lists (Purpose): the state diagram of `components/entity/lottery-entry` gains Won --> Lost, and the usecase diagram of `stories/win-tickets-in-a-lottery` names `LotteryEntryUseCase.Draw`, `LotteryEntryUseCase.DrawDueSales`, `OrderUseCase.Issue` and `CardAuthorizationUseCase.Release` instead of the removed methods; delete the emptied `persist-draw-outcome`, `list-lottery-entry-ids-awaiting-issuance`, `run-draw`, `issue-from-captured-win` and `issue-due-wins` specs; verify `openspec validate --specs` passes
