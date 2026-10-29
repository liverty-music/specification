## 1. Prerequisites

- [ ] 1.1 Confirm `introduce-durable-workflows` is released in backend and `workflow-worker` runs in prod; verify `kubectl get deploy workflow-worker -n backend` shows 1/1 ready
- [ ] 1.2 Confirm `remodel-ticket-sales` and `publish-events-through-outbox` are released in backend (Orders created Pending with their LotteryEntry, TicketStock; entity operations announce through the outbox; `LotteryEntry.lost_reason`) and their specs are archived; verify `openspec validate make-lottery-draw-durable --strict` passes against the archived main specs

## 2. Entity operations (components/entity/lottery-entry/persist-draw-outcome, revert-win, send-loss-email, components/entity/card-authorization/capture, release)

- [ ] 2.1 Add the migration for `lottery_entries.loss_email_send_at` (TIMESTAMPTZ, commented) and add `lottery_loss` to the `notifications.type` comment; verify `make lint-schema` passes and the migration applies to a local database
- [ ] 2.2 Change `PersistDrawOutcome` to take each stock's entries in draw order, lock each `ticket_stocks` row and admit against the remaining count it reads, and to leave entries that are no longer Entered unchanged (no draw time: remodel-ticket-sales D12) (design "Record first, then one workflow per entry"); verify the contract tests "Outcome recorded", "Failure leaves nothing recorded", "Empty draw", "Tickets taken since the order was fixed" and "Recorded again" pass, and that only the entries it changes are announced, plus an rdb test that commits a Checkout on the stock between ordering and recording
- [ ] 2.3 Declare and implement `LotteryEntry.RevertWin` (entry Lost with the lost reason "card could not be charged", Order Void and the entry's announcement in one transaction, `# Announces` in its Go doc); verify the contract tests "Win reverted", "Already reverted", "Win already issued", "Not drawn", "Unknown entry", "Win reverted and announced", "Already reverted announces nothing" and "Announcement cannot be recorded" pass
- [ ] 2.4 Declare and implement `LotteryEntry.SendLossEmail`; verify the contract tests "Email sent", "Redelivered event", "Mail unavailable" pass
- [ ] 2.5 Stop sending the fixed idempotency keys on capture and cancel in `stripe_card_authorization.go` (design "Stripe keys: the operation, not the run"); verify the contract tests "Payment provider error, then recovered" of capture and release pass against a stub that answers the first call with a 500 and replays it for the same key, and the existing capture and release tests still pass
- [ ] 2.6 Remove `Order.ListLotteryEntryIDsAwaitingIssuance` with its tests and mocks; verify `make check` passes with no reference left

## 3. Usecases (components/usecase/lottery-entry/draw, draw-due-sales, components/usecase/order/release-card-authorization, issue, fulfill-payment)

- [ ] 3.1 Implement `LotteryEntryUseCase.Draw` as a workflow (design "Record first, then one workflow per entry") and remove `RunDraw`; verify one unit test per scenario passes with mocked `Flow` and operations ("Winners and losers recorded", "Each stock is drawn against its own remaining tickets", "Losers in draw order", "No entries", "Stopped before the outcome was recorded"), and that it starts no other workflow
- [ ] 3.2 Change `DrawDueSales` to a scheduled workflow that starts `draw:<sale>`; verify the unit tests "Window closes", "Window still open", "Drawn once", "One sale fails" pass
- [ ] 3.3 Implement `OrderUseCase.ReleaseCardAuthorization` for a Void Order as a workflow with a 24-hour deadline; verify the unit tests "Loser released", "Win reverted", "Order not Void", "Payment provider unavailable", "Payment provider unavailable for a day", "Charged card authorization" pass
- [ ] 3.4 Implement `OrderUseCase.Issue` for a LotteryEntry as a workflow with a 24-hour deadline, on the `payment` queue (global concurrency 2), making the Pending Order Paid with `Order.Issue`, and remove `IssueFromCapturedWin` and `IssueDueWins`; verify one unit test per scenario of "Every Won entry is issued", "Charge, then issue" and "Identity verification binding" passes
- [ ] 3.5 Change `OrderUseCase.FulfillPayment` to succeed without effect for a LotteryEntry; verify the unit tests of "Each completed charge ends in an issued Order" pass, including "Lottery win charged"
- [ ] 3.6 Remove the lottery draw and issuance goroutines from `internal/di/provider.go` and register the workflows, the queue and the `draw-due-sales` schedule in `cmd/worker`; verify `make check` passes and `/worker workflow list` shows the schedule runs locally

## 4. Notifications (components/usecase/notification/send-lottery-loss, send-order-confirmation, deliver)

- [ ] 4.0 In the `ORDER.lottery_entry_drawn` consumer, start `OrderUseCase.Issue` (`issue:<order>`) for a Won entry's Order and `OrderUseCase.ReleaseCardAuthorization` (`release:<order>`) for a Lost entry's Order with `Workflows.Start`, as a durable consumer of its own (design "Record first") (design "The work after the draw starts from the entries' announcements"); verify a unit test that a delivery repeated with the same id starts each workflow once, and that an entry announced Lost by `RevertWin` starts its release
- [ ] 4.1 Implement `NotificationUseCase.SendLotteryLoss` on the `ORDER.lottery_entry_drawn` consumer for entries announced Lost, reading the lost reason from the entry, in a durable consumer of its own (separate from the workflow starter of 4.0), and starting Deliver as `deliver:lottery_loss:<entry>` with the `lottery_loss` type; verify the unit tests "Entry not drawn", "Card could not be charged", "Loss announced twice", "Mail unavailable", "Fan allowed notifications" and the Deliver test "Lottery loss sent" pass
- [ ] 4.2 Add the win wording to the confirmation email and push for an Order whose source is a LotteryEntry, in Japanese and English; verify the unit tests "Lottery win" and "Lottery winner allowed notifications" pass

## 5. Story (stories/win-tickets-in-a-lottery)

- [ ] 5.1 Extend `lottery_story_integration_test.go` to run the lottery through the workflows against local Postgres and a fake payment provider; verify "Demand within quantity", "Oversubscribed sale", "Stopped after the first charge" (stop the worker after the first capture, start it again, assert the same winners, one charge each, 2 Issued Tickets each, the loser never charged) and "Card closed before the charge" pass, with one email per fan
- [ ] 5.2 Run `make test-stripe-e2e` with the Stripe Sandbox key and confirm the authorize and capture legs still pass

## 6. Release and production check

- [ ] 6.1 Read-only in prod before the deploy, list Lottery sales due for a draw and Won entries whose Order is Pending; record the counts in design.md and stop if such a Won entry exists (design "Migration Plan")
- [ ] 6.2 Merge the backend PR, cut the release, and confirm in prod (read-only) that the AtlasMigration applied, `workflow-worker` rolled out, and `/worker workflow list` shows a `draw-due-sales` run for each minute since the rollout
- [ ] 6.3 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the run succeeds

## 7. Archive

- [ ] 7.1 Delete the emptied `list-lottery-entry-ids-awaiting-issuance`, `run-draw`, `issue-from-captured-win` and `issue-due-wins` specs; verify `openspec validate --specs` passes
- [ ] 7.2 In the usecase diagram of `stories/win-tickets-in-a-lottery`, name `OrderUseCase.ReleaseCardAuthorization` instead of `LotteryEntryUseCase.ReleaseCardAuthorization` (kept until this change ships, so the main spec names no method of a later change); verify `openspec validate --specs` passes
