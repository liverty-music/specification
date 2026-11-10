# Tasks

The order across repositories is design.md decision 3: cloud-provisioning PR 1, then backend, then cloud-provisioning PRs 2 and 3. specification docs can land at any time.

## 1. cloud-provisioning: new streams and moved durables (PR 1)

- [ ] 1.1 Add Stream CRs for EVENT, FOLLOW, PASSKEY, PUSH_SUBSCRIPTION, TICKET_SALE, LOTTERY_ENTRY, RESALE_ENTRY, RESALE_LISTING, CHECKOUT and TICKET under `k8s/namespaces/nats/base/jetstream/`, with the settings of the existing streams and the per-environment replica overrides. Register them in the kustomization. Verify with `kubectl kustomize` for both overlays.
- [ ] 1.2 Edit every Consumer CR to the stream and `filterSubject`/`filterSubjects` of design.md decision 1, and rename the CRs and durables of the renamed behaviors (decision 1, "Renamed durables"). Keep `TICKET_JOURNEY.status_changed` in `track-ticket-journey`'s `filterSubjects` next to the five new subjects (decision 3, step 1). Verify with `kubectl kustomize` that every behavior of the backend's new behavior table has exactly one CR with a matching durable, stream and filter.
- [ ] 1.3 Add KEDA triggers for every new (stream, durable) pair in `event-consumer/scaledobject.yaml` and its prod overlay, keeping the old triggers. Verify with `kubectl kustomize`.
- [ ] 1.4 After the merge and the ArgoCD sync, run `nats stream ls` and `nats consumer ls <stream>` read-only from the nats-box in prod. Verify that every new stream and durable exists and that the old durables are still there.

## 2. backend: subjects, streams and consumers

- [ ] 2.1 Rename and re-value the subject constants in `internal/entity/event_data.go` to decision 1. Rewrite their doc comments from the specs, and update `AllSubjects`. Update `internal/infrastructure/messaging/streams.go` and `testdata/jetstream_stream_subjects.txt` to one stream per entity, without VENUE and TICKET_EMAIL. Verify with the stream-coverage test in `streams_test.go`.
- [ ] 2.2 Announce one subject per state. LotteryEntry.PersistDrawOutcome, RevertWin and EndEnteredByEvent announce LOTTERY_ENTRY.won and .lost. ResaleEntry.PersistDrawOutcome, RevertWin and Withdraw announce RESALE_ENTRY.won, .lapsed, .lost and .withdrawn. TicketJourney.Upsert and UpsertIfReplaceable announce TICKET_JOURNEY.<status>. Verify with the contract tests carrying `@spec` for the modified scenarios of the lottery-entry, resale-entry and ticket-journey operation specs: each asserts the subject of the announcement it expects.
- [ ] 2.3 Point every other announcing repository at its renamed constant. Update the contract tests carrying `@spec` for the remaining modified operation specs (artist, checkout, concert, series, follow, order, organizer, passkey, push-subscription, resale-listing, series-image, ticket, ticket-sale, user) to assert the new subject. Verify with `make check`.
- [ ] 2.4 Update the behavior table in `internal/di/consumer.go` to the durable names and subject lists of decision 1. Let a behavior take several subjects of one stream (decision 2), and have the lottery, resale and journey handlers tell the state from the subject. Rename the consumer files and types that carry old event names (`lottery_entry_drawn_consumer.go`, `resale_entry_consumer.go`, `ResaleEntryChanged...`). Verify with the consumer unit tests, including one per state for `start-resale-entry-workflow`, `send-resale-entry-ended`, `start-lottery-entry-workflow` and `send-lottery-loss`, and with the health test listing the new durables.
- [ ] 2.5 Update `TicketJourneyUseCase.MarkApplied`'s trigger to LotteryEntry.Entered. Verify with its unit test carrying `@spec` for the modified mark-applied scenarios.
- [ ] 2.6 Run `git grep` for every old subject string, old stream name and old durable name in the backend. Verify that nothing is found.
- [ ] 2.7 Before the rollout, check read-only in prod that `watermill_events_outbox` has no row and every old durable has 0 pending messages (design.md decision 3, step 2). After the rollout, check that every old durable still has 0 pending messages and that event-consumer is healthy with the new durables bound. Republish any pending message to its new subject (step 4).

## 3. cloud-provisioning: remove what is left behind (PRs 2 and 3)

- [ ] 3.1 Set `preventDelete: false` on the Stream CRs of SALES_PHASE, NOTIFICATION, VENUE and TICKET_EMAIL and on the Consumer CR of track-ticket-email, remove the old KEDA triggers, and drop `TICKET_JOURNEY.status_changed` from `track-ticket-journey` (PR 2). Verify with `kubectl kustomize` and, after the sync, that NACK reports the CRs as reconciled.
- [ ] 3.2 Remove those CRs (PR 3). After the sync, verify with `nats stream ls` that the four streams are gone.
- [ ] 3.3 On ORDER, CONCERT, ARTIST, USER and ORGANIZER, list the durables with `nats consumer ls`, and delete by hand, once, with `nats consumer rm` from the nats-box, only those that design.md decision 1 does not place on that stream (decision 3, step 7). Verify that `nats consumer ls` on each lists exactly the durables of decision 1.
- [ ] 3.4 Rewrite the comments in `k8s/namespaces/backend/base/cronjob/sales-phase-discovery/configmap.env`, `cronjob/sales-reminders/configmap.env`, `overlays/prod/kustomization.yaml` and `src/zitadel/constants.ts` that name old or nonexistent subjects. Verify that `git grep` for every old subject string and stream name finds nothing.

## 4. specification: docs and proto comment

- [ ] 4.1 Update `docs/event-delivery-design.md`, the subject column of `docs/analytics/event-catalog.md`, and the CONCERT.cancelled comment in `proto/liverty_music/rpc/organizer/series/v1/series_service.proto` to the new events and subjects. Verify that `git grep` for every old subject string finds nothing outside `openspec/changes/archive/`, and that `buf lint` passes.
- [ ] 4.2 When archiving, after add-flow-diagrams-to-specs has merged its Purpose edits, edit directly in the main specs: the events tables of LotteryEntry, ResaleEntry and TicketJourney to the split events, the SeriesImage table to add SeriesImage.Uploaded, and every story diagram that draws LotteryEntry_Drawn, ResaleEntry_Changed or TicketJourney_StatusChanged (design.md decision 5). Verify that `python3 scripts/check-diagrams.py` and `openspec validate --specs` pass.
