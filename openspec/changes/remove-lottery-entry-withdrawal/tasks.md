## 1. Proto (specification)

- [ ] 1.1 Delete `LotteryEntryService.Withdraw`, `WithdrawRequest` and `WithdrawResponse` from `proto/liverty_music/rpc/lottery_entry/v1/lottery_entry_service.proto`, add `reserved 4; reserved "LOTTERY_ENTRY_STATE_WITHDRAWN";` to `LotteryEntryState` in `proto/liverty_music/entity/v1/lottery_entry.proto`, and rewrite the comments that describe withdrawal (design "Proto"); verify `buf lint` and `buf format -d` report nothing
- [ ] 1.2 Open the specification PR with the `buf skip breaking` label, merge it once `CI Success` passes, cut the Release and confirm `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Schema migration (backend)

- [ ] 2.1 Read-only, through the prod `db-proxy` runbook, list the `lottery_entries` rows with `state = 4` and their `card_authorization_id`; for each authorization still uncaptured, cancel it once by hand in the Stripe Dashboard (a one-time action, design "Risks"); record the row count and the cancelled ids in this change's design.md
- [ ] 2.2 Add the Atlas migration of design "Schema migration" (delete Withdrawn rows, replace `uq_lottery_entries_active` with `uq_lottery_entries_ticket_type_user`, replace `chk_lottery_entries_state` and `chk_lottery_entries_authorized_from_entered`, update the comments); verify `atlas migrate lint` passes and the migration applies to a local database holding a Withdrawn row and its Referral

## 3. Entity (components/entity/lottery-entry)

- [ ] 3.1 Remove `LotteryEntryStateWithdrawn`, `IsActive` and `IsWithdrawable` from `internal/entity/lottery_entry.go` and their String and mapper cases; verify `make check` passes
- [ ] 3.2 Update the entity unit tests for "Confirmable only as a Draft with a card authorization" (scenarios "Draft with a card authorization", "Draft without a card authorization", "Already entered" over Entered, Won and Lost) and delete the tests of the removed requirements; verify they pass

## 4. Entity operations (components/entity/lottery-entry/*, components/entity/order/list-lottery-entry-ids-awaiting-issuance)

- [ ] 4.1 Change `GetOrCreateDraft` to update a Draft with another count in place, remove its card authorization and return the removed id, under the existing `FOR UPDATE` lock (design "A count change updates the Draft in place"); verify one contract test per scenario of "At most one entry per account per ticket type" passes ("First start", "Reload with the same count", "Count changed", "Double tap", "Already entered", "Entry for another event of the same sale", "Unknown ticket type")
- [ ] 4.2 Drop the Draft argument and the Withdrawn update from `PersistDrawOutcome`; verify the contract tests "Outcome recorded" (the Draft is still a Draft), "Failure leaves nothing recorded" and "Empty draw" pass
- [ ] 4.3 Remove the `state <> 4` filters from the other lottery entry queries and update the contract tests: `Get` ("Existing entry", "Unknown id"), `ListByTicketTypeAndUser` ("Entry of the user", "Never entered"), `GetStatsByTicketType` ("After the draw", "Draft entries excluded", "No entries"), `ListUndrawnForTicketType` ("Mixed states", "No candidates"), `UpdateState` ("State changed", "Unknown id") and `Order.ListLotteryEntryIDsAwaitingIssuance` ("Won without order", "Already issued", "Not won"); verify the rdb integration tests pass

## 5. Usecases (components/usecase/lottery-entry/*, components/usecase/order/issue-from-captured-win)

- [ ] 5.1 Delete `LotteryEntryUseCase.Withdraw`, its tests and its mock; verify `make check` passes with no remaining reference
- [ ] 5.2 Change `LotteryEntryUseCase.Start` to release the card authorization `GetOrCreateDraft` removed, and on a failed release to log `LogKeyNeedsOperator` with its id and still return the Draft (design "The release happens after the change"); verify one unit test per scenario of "Start or change an entry while the window is open" passes, including "Count changed after authorizing" and "Release fails on a count change"
- [ ] 5.3 Change `LotteryEntryUseCase.RunDraw` to stop passing Drafts to `PersistDrawOutcome` while still releasing their card authorizations; verify the unit tests "Unconfirmed draft at the draw" (the Draft stays a Draft) and "No entries" pass with the rest of "Draw a sale"
- [ ] 5.4 Update the `IssueFromCapturedWin` unit test "Entry not won" to Draft, Entered and Lost; verify it passes

## 6. Adapter (components/adapter/fan/api/rpc/lottery-entry)

- [ ] 6.1 Upgrade the generated package to the new BSR version, delete `LotteryEntryHandler.Withdraw` and its tests, and update the handler tests for "Every lottery entry call is made by the signed-in fan" ("Fan starts an entry", "Not signed in", "Caller without an account") and "Lottery entry requests are validated at the boundary"; verify `make check` passes

## 7. Story (stories/win-tickets-in-a-lottery)

- [ ] 7.1 In `lottery_story_integration_test.go`, delete the test of "Withdraw and enter again", annotate the existing unconfirmed-Draft test with `@spec stories/win-tickets-in-a-lottery "Entry left unconfirmed"` under the new requirement, and add a test for "Count changed before confirming" (the first card authorization is released and only the 3-ticket entry takes part); verify the story integration tests pass

## 8. Frontend (lottery entry status screen)

- [ ] 8.1 Upgrade the generated package, remove the withdraw action, its confirm step and its i18n keys from `lottery-entry-status-route`, and remove the `withdrawn` value and result from `entities/lottery-entry.ts` and the route; verify the route's component tests pass and `make check` is clean
- [ ] 8.2 Run the lottery entry status screen with Playwright on a local build against a stubbed `ListByTicketType`: an Entered entry shows the waiting state with no withdraw action, and Won and Lost entries show their result

## 9. Release and production check

- [ ] 9.1 Merge the backend PR, cut the release and confirm in prod (read-only) that the AtlasMigration is applied, `uq_lottery_entries_ticket_type_user` exists, no `state = 4` row remains, and the fan-api rollout finished
- [ ] 9.2 Merge the frontend PR, cut the release, confirm the rollout, and run `gh workflow run stripe-sandbox-e2e.yml`; confirm the run succeeds

## 10. Archive

- [ ] 10.1 Edit the main spec Purposes this change lists (Purpose): the state row and the state diagram of `components/entity/lottery-entry` without Withdrawn; the usecase diagram of `stories/win-tickets-in-a-lottery` without `LotteryEntryUseCase.Withdraw`; the Purpose sentences of `components/entity/lottery-entry/list-undrawn-for-ticket-type` and `persist-draw-outcome` without "withdraws" and "Withdrawn"; delete the emptied `components/usecase/lottery-entry/withdraw` spec; verify `openspec validate --specs` passes
