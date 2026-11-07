## 1. Lost reason (specification)

- [ ] 1.1 Append `LOTTERY_ENTRY_LOST_REASON_CONCERT_CANCELLED = 3` to `LotteryEntryLostReason` in `proto/liverty_music/entity/v1/lottery_entry.proto` (design D4); verify `buf lint` and `buf breaking` pass, merge, cut the specification release and confirm BSR gen succeeds

## 2. Durable consumer (cloud-provisioning)

- [ ] 2.1 Add the NACK Consumer manifest `consumer-end-lottery-entries-of-cancelled-event.yaml` (stream `CONCERT`, filter `CONCERT.cancelled`, settings as `consumer-send-event-cancelled.yaml`) to `k8s/namespaces/nats/base/jetstream/` and its `kustomization.yaml` (design D6); verify `kustomize build` renders it, merge, and confirm in prod (read-only) that the Consumer exists on the `CONCERT` stream

## 3. Schema and entity (backend)

- [ ] 3.1 Count Entered lottery entries of CANCELLED Events in prod through the read-only runbook (design Migration Plan); zero lets the work go on, any other count stops it to ask how to end them
- [ ] 3.2 Upgrade the backend schema package to the release of task 1.1, add `LotteryEntryLostReasonConcertCancelled`, and map it in `lotteryEntryLostReasonToProto` and `LotteryEntryFromAnnouncement` (design D4); verify a unit test that an announcement round-trips the new reason
- [ ] 3.3 Widen `chk_lottery_entries_lost_reason` to `IN (1, 2, 3)` and update the column comment in a versioned migration; verify the migration applies to local Postgres, and that a Lost entry with lost reason 3 is accepted while 4 is refused

## 4. Entity operations (components/entity/lottery-entry/end-entered-by-event, revert-win)

- [ ] 4.1 Declare `EndEnteredByEvent` on `entity.LotteryEntryRepository` with a `# Announces` doc section and implement it in `lottery_entry_repo.go` (design D2); verify one contract test per scenario against local Postgres: Entries of a cancelled event, Won entry, Another date of the series, Called again, No entries, Two entries ended, Called again announces nothing, Announcement cannot be recorded
- [ ] 4.2 Make `RevertWin` take the lost reason (design D3) and pass "card could not be charged" from the existing caller; verify the contract tests Win reverted, Win reverted for a cancelled concert, Already reverted, Win already issued, Not drawn, Unknown entry, Win reverted and announced, Already reverted announces nothing and Announcement cannot be recorded pass

## 5. Usecases (components/usecase/lottery-entry/end-for-cancelled-event, authorize-card, confirm, components/usecase/order/issue, release-card-authorization, components/usecase/notification/send-lottery-loss)

- [ ] 5.1 Implement `LotteryEntryUseCase.EndForCancelledEvent`; verify unit tests Concert cancelled during the window, Announcement delivered twice and Store unavailable pass with the operation mocked
- [ ] 5.2 Make `AuthorizeCard` and `Confirm` read `Event.IsEventPublished`, `Confirm` refusing through its existing release path; verify unit tests "Concert cancelled" of authorize-card and "Concert cancelled during card authentication" of confirm pass, and that the existing scenarios of both specs still pass
- [ ] 5.3 Add the check to `issueEntry`'s capture step (design D3), leaving `issueCheckout` unchanged; verify unit tests Lottery concert cancelled before the charge, Concert cancelled while the payment provider is unavailable, Earlier attempt charged, then concert cancelled and Card authorization no longer chargeable pass, and that the Issue workflow tests of a placed Checkout are unchanged
- [ ] 5.4 Confirm `ReleaseCardAuthorization` and `StartDrawnEntryWorkflow` handle a Lost entry of the new reason with no change; verify the unit test "Entry of a cancelled concert released" passes
- [ ] 5.5 Add the wording of design D5 to `lottery_loss.go`; verify unit tests Concert cancelled email and Concert cancelled push of send-lottery-loss pass in ja and en, and that "Entry not drawn" and "Card could not be charged" are unchanged

## 6. Receiver (backend)

- [ ] 6.1 Add the handler that decodes the Event and calls `EndForCancelledEvent`, and register it as `end-lottery-entries-of-cancelled-event` on `entity.SubjectConcertCancelled` in `internal/di/consumer.go` (design D6); verify a consumer unit test that an announced Event reaches the usecase, that a payload with no id is refused, and that a usecase failure is returned so the message is redelivered

## 7. Stories and release (stories/win-tickets-in-a-lottery, stories/remove-a-cancelled-concert)

- [ ] 7.1 Extend the `win-tickets-in-a-lottery` story integration test, against local Postgres with the worker running, a stub mail server and a stub payment provider; verify Cancelled during the window, Cancelled between the draw and the charge, Entering after the cancellation and Another date of the sale pass
- [ ] 7.2 Extend the `remove-a-cancelled-concert` story integration test; verify Deleted during the window passes
- [ ] 7.3 Merge the backend PR, cut the release, and confirm in prod (read-only) that the AtlasMigration applied, the constraint allows 3, and `event-consumer` rolled out and bound to the new durable
- [ ] 7.4 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the run succeeds

## 8. Archive

- [ ] 8.1 Confirm the PRs of tasks 1.1, 2.1 and 7.3 are merged and cite them, and close liverty-music/specification#1240 with a note that its premise was wrong and what shipped instead
- [ ] 8.2 Edit the Purpose of the main specs, kept until this change ships so they describe only shipped behavior: `components/entity/lottery-entry` (the lost reason attribute gains "concert cancelled"), `components/entity/lottery-entry/revert-win` (a win is reverted for a card that cannot be charged or a cancelled concert), and the usecase diagram of `stories/win-tickets-in-a-lottery` (`LotteryEntryUseCase.EndForCancelledEvent`); verify `openspec validate --specs` passes
