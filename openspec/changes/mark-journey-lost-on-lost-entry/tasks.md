## 1. cloud-provisioning: the consumer of lost lottery entries (design "A consumer of LOTTERY_ENTRY.lost")

- [ ] 1.1 Add `consumer-mark-ticket-journey-lost.yaml` (`streamName: LOTTERY_ENTRY`, `filterSubject: LOTTERY_ENTRY.lost`, the other settings of `consumer-mark-ticket-journey-applied.yaml`) to the JetStream kustomization and its trigger to the event-consumer ScaledObject; verify `kustomize build` of the prod overlays lists both, merge, and after ArgoCD syncs prod confirm read-only that the consumer exists

## 2. backend (components/entity/ticket-journey, components/usecase/ticket-journey/mark-lost)

- [ ] 2.1 Make `ReplaceableBy` refuse a platform Lost over Unpaid, Paid and Lost; verify one table-test case per scenario of "Which journeys the platform and the app may replace", and the contract tests of `entity/ticket-journey/upsert-if-replaceable` still pass
- [ ] 2.2 Add `TicketJourneyUseCase.MarkLost` over the lost reason, `Order.GetHeldForEvent` and `UpsertIfReplaceable`; verify one unit test per scenario of `usecase/ticket-journey/mark-lost` with the operations mocked
- [ ] 2.3 Add the `mark-ticket-journey-lost` consumer of `LOTTERY_ENTRY.lost` in `event-consumer`; verify a consumer test that a failed MarkLost nacks the message
- [ ] 2.4 Add the story test covering both scenarios of "A lost entry marks the fan's journey Lost" in `stories/win-tickets-in-a-lottery` and verify it passes
- [ ] 2.5 Open the backend PR, merge, release; confirm read-only in prod that the release is rolled out and the `mark-ticket-journey-lost` consumer is bound with no pending or redelivering messages

## 3. specification: Purposes

- [ ] 3.1 At archive, edit the Purposes of `entity/ticket-journey`, `entity/ticket-journey/upsert-if-replaceable` and `stories/win-tickets-in-a-lottery` (add the MarkLost frame after `LotteryEntry_Lost` to its diagram), and verify `openspec validate --specs` and `scripts/check-diagrams.py` pass
