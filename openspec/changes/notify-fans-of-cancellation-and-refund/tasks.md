## 1. Durable consumers (cloud-provisioning)

- [ ] 1.1 Add NACK Consumer manifests `consumer-send-event-cancelled.yaml` (stream `CONCERT`, filter `CONCERT.cancelled`) and `consumer-send-order-refunded.yaml` (stream `ORDER`, filter `ORDER.refunded`) to `k8s/namespaces/nats/base/jetstream/` and its `kustomization.yaml` (design D6); verify `kustomize build` succeeds, merge, and confirm in prod (read-only) that both Consumers are Ready before task 6.2

## 2. Schema (backend)

- [ ] 2.1 Read-only in prod, count Refunded Orders (design "Migration Plan" step 1); record the count in design.md and stop if it is above 0
- [ ] 2.2 Add `order_refunds` and drop `orders.provider_refund_id` in `schema.sql` with its `COMMENT ON` lines, add `event_cancelled` and `order_refunded` to the `notifications.type` comment, and generate the Atlas migration (design D1); verify `make lint-schema` passes and the migration applies to a local database

## 3. Entity operations (components/entity/order/commit-refund, send-cancellation-email, send-refund-email, components/entity/series/cancel-events)

- [ ] 3.1 Add `OrderRefund` to the Order entity and read it in `order_repo.go`, `checkout_repo.go` and `lottery_entry_repo.go` with a LEFT JOIN, mapping the proto `provider_refund_id` from it (design D1); verify the existing repository and adapter tests pass
- [ ] 3.2 Change `CommitRefund` to take the reason, the amount and the time, store the `order_refunds` row and announce `ORDER.refunded` only when the guarded Order update changed a row, with `# Announces` in its Go doc (design D2); verify one contract test per scenario of `entity/order/commit-refund` passes against local Postgres ("Refund recorded", "Ticket on resale", "Ticket resold earlier", "No settlement", "Dispute recorded", "Reason missing", "Settlement already reversed", "Failure changes nothing", "Refund announced", "Recorded twice", "Announcement cannot be recorded")
- [ ] 3.3 Announce `CONCERT.cancelled` per Event `CancelEvents` makes CANCELLED, with `# Announces` in its Go doc (design D2); verify the contract tests "Two dates cancelled", "Draft removed" and "Announcement cannot be recorded" pass, and the existing CancelEvents tests still pass
- [ ] 3.4 Declare `SendCancellationEmail` and `SendRefundEmail` on the Order mailer interface and implement them in the Postmark mailer (design D5); verify the contract tests of `send-cancellation-email` ("Email sent", "Address missing", "Mail unavailable") and of `send-refund-email` ("Email sent", "Message missing", "Mail unavailable") pass against a stub mail server

## 4. Usecases (components/usecase/order/refund, components/usecase/notification/send-event-cancelled, send-order-refunded, deliver)

- [ ] 4.1 Pass the reason, the refunded amount and the time from `Refund` to `CommitRefund`; verify the unit tests "Tickets voided", "Cancellation refund recorded", "Dispute recorded", "Concurrent refund" and "Retry after a failure" pass
- [ ] 4.2 Add `NotificationUseCase.SendEventCancelled`, which lists the Event's Orders and starts the workflow `notify-event-cancelled:<order>` (read, email, then Deliver `deliver:event_cancelled:<order>`) for each Paid Order (design D3, D4); verify one unit test per scenario passes with mocked operations and `Workflows`: "Two buyers", "Already refunded", "Cancellation announced twice", "No buyer", "Cancellation email", "One ticket resold", "Fan allowed notifications", "Refunded before the notice", "Event deleted before the notice", "Mail unavailable"
- [ ] 4.3 Add `NotificationUseCase.SendOrderRefunded`, which starts the workflow `notify-order-refunded:<order>` (read, email, then Deliver `deliver:order_refunded:<order>`) (design D3, D4); verify one unit test per scenario passes: "Refund email", "One ticket resold", "Every ticket resold", "Dispute", "Fan allowed notifications", "Refund announced twice", "Event deleted before the notice", "Mail unavailable"
- [ ] 4.4 Add the notification types `event_cancelled` and `order_refunded` (design D5); verify the Deliver tests "Cancellation sent" and "Refund sent" pass

## 5. Receivers (backend)

- [ ] 5.1 Add the `CONCERT.cancelled` and `ORDER.refunded` consumers, which only decode the payload and call `SendEventCancelled` or `SendOrderRefunded`, register them as `send-event-cancelled` and `send-order-refunded` in `internal/di/consumer.go`, and register both workflows in `cmd/worker` (design D6); verify a unit test that a delivery repeated with the same Order starts each workflow once, and `make check` passes

## 6. Story and release (stories/remove-a-cancelled-concert)

- [ ] 6.1 Add a `remove-a-cancelled-concert` story integration test (none exists yet) that cancels an Event with two Paid Orders, refunds both and deletes the Event, against local Postgres with the worker running and a stub mail server; verify "Cancelled and refunded" and "Deleted right after the refunds" pass, each fan receiving one cancellation email and one refund email
- [ ] 6.2 Merge the backend PR, cut the release, and confirm in prod (read-only) that the AtlasMigration applied, `orders.provider_refund_id` is gone, `order_refunds` exists, and `workflow-worker` and `event-consumer` rolled out
- [ ] 6.3 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the run succeeds

## 7. Archive

- [ ] 7.1 Confirm the PRs of tasks 1.1 and 6.2 are merged and cite them
- [ ] 7.2 Edit the Purpose of the main specs `components/entity/order` (attributes refund reason, refund amount, refund time; provider refund ID present only for a 中止 refund that moved money) and `components/entity/notification` (types `event_cancelled`, `order_refunded`), kept until this change ships so the main specs describe only shipped behavior; verify `openspec validate --specs` passes
