## Context

See proposal.md - Why. The current state this design builds on (backend `54a485a8`):

- `SeriesRepository.CancelEvents` (`series_events_repo.go:550`) makes PUBLISHED Events CANCELLED in one transaction and announces nothing. `publish-events-through-outbox` removed the `CONCERT.cancelled` subject because it had no receiver; the `CONCERT` stream still takes `CONCERT.*`.
- `OrderUseCase.Refund` (`order_refund_uc.go:45`) computes the refunded amount (`unresoldAmount`), moves the money, then calls `RefundRepository.CommitRefund` (`refund_repo.go:90`). `CommitRefund` updates `tickets`, `resale_listings`, `settlements` and `orders` (`status`, `provider_refund_id`) in one transaction and announces nothing. The reason, the amount and the time are not stored.
- The admin console's `Refund all` calls `OrderService.Refund` once per Paid Order (`admin/artist-concerts/artist-concerts-route.ts:234`), and an admin can `Delete` the Event right after; the deletion removes its Refunded Orders (`event_removal.go`).
- Existing notices keep one email per entity with a send-time column (`orders.confirmation_send_at`, `lottery_entries.loss_email_send_at`) and one push with the Deliver workflow name `deliver:<type>:<id>`. Receivers with no row of their own instead start a workflow named after a business key and send the email inside it (`publish-events-through-outbox` design, the passkey and verification emails).

## Goals / Non-Goals

**Goals:**
- One cancellation notice and one refund notice per Order, with no send-time column.
- A refund record that receipts and bookkeeping can read later, with no column that is NULL for every Order not refunded.

**Non-Goals:**
- A notice for a dispute. `dispute-representment` changes that flow.
- A guard that refuses `Delete` while a notice is unsent (decided with the user, 2026-11-06).
- Showing the refund amount on the fan's order screen or in the admin console.
- Releasing open lottery entries of a cancelled Event (#1240).

## Decisions

### D1. The refund record is its own table; the Order spec carries it as attributes

`order_refunds (order_id PK REFERENCES orders ON DELETE CASCADE, reason SMALLINT NOT NULL, amount BIGINT NOT NULL, provider_refund_id TEXT, refund_at TIMESTAMPTZ NOT NULL)`, with `CHECK (reason IN (1, 3))` (the values of `usecase.RefundReason`: 1 Cancellation, 3 Dispute; 2 is retired), `CHECK (amount >= 0)` and `CHECK (provider_refund_id IS NULL OR provider_refund_id <> '')`. `orders.provider_refund_id` moves into it: a row exists exactly for a Refunded Order. `provider_refund_id` is NULL when no money moved (a dispute, or every ticket resold); that absence is the fact "the platform issued no refund", so it stays nullable.

- Alternative: five nullable columns on `orders` with one CHECK tying them to `status = 2`. Rejected in review: every Paid, Pending and Void Order carries NULLs that only repeat what `status` says.
- Alternative: a new entity `Refund` with its own spec and proto message. Rejected: every rule of the record is about the Order (one refund per Order, only from Paid), so in the spec it is attributes of Order; the separate table is storage only.
- Cost: "Refunded ⇔ a row exists" spans two tables, so no CHECK can hold it. `CommitRefund` writes both in one transaction and is the only writer; a contract test reads both after each scenario.
- The Go `entity.Order` gains `Refund *OrderRefund` (reason, amount, provider refund ID, time). `order_repo.go`, `checkout_repo.go` and `lottery_entry_repo.go` read `o.provider_refund_id` today; they LEFT JOIN `order_refunds`. The proto `Order.provider_refund_id` keeps its field and meaning and is filled from the record, so no proto change.

### D2. CancelEvents and CommitRefund announce, in their transactions

- `CancelEvents` announces `CONCERT.cancelled` once per Event it makes CANCELLED, with the Event (`pb.FromEvent`) as the payload, after `cancelEventsQuery` and before the commit. A removed DRAFT Event is not announced. The `CONCERT` stream already takes `CONCERT.*`.
- `CommitRefund` changes `UPDATE orders SET status = 2 ... WHERE id = $1` to a guarded `... AND status = 1`, inserts the `order_refunds` row only when that update changed a row, and then announces `ORDER.refunded` with the Order (`pb.FromOrder`). When the update changes nothing and no Settlement is given, the Order is already Refunded: it returns without change or announcement. The existing Settlement guard (`FailedPrecondition` on a Reversed Settlement) stays.
- Check then act: the guarded `UPDATE ... WHERE status = 1` takes the Order's row lock, so two concurrent `CommitRefund` calls cannot both insert the record or announce. Nothing else creates `order_refunds` rows.

### D3. Once per Order through workflow names, not send times

- The `CONCERT.cancelled` receiver only decodes the Event and calls `NotificationUseCase.SendEventCancelled`, as `lottery_entry_drawn_consumer.go` calls `OrderUseCase.StartDrawnEntryWorkflow` (backend `AGENTS.md`: adapters map types and call usecases). `SendEventCancelled` lists the Event's Orders (`Order.ListByEvent`) and starts the per-Order notice for each Paid Order as the workflow `notify-event-cancelled:<order>`. The `ORDER.refunded` receiver calls `SendOrderRefunded`, which starts its notice as `notify-order-refunded:<order>`. A repeated announcement starts nothing new.
- Each workflow reads what the message needs in its first step, sends the email in a second step, and starts Deliver as `deliver:<type>:<order>` for the push. A completed step does not run again, so a stop after the email does not send it twice. A stop during the email step can send it twice, the same as with a send time today.
- Alternative: send-time columns (`cancellation_email_send_at`, `refund_email_send_at`) as in `SendOrderConfirmation`. Rejected in review: the workflow name already gives "once", and a column only for bookkeeping has no spec field to map to (backend `AGENTS.md`: every new column maps to an entity field the spec defines).
- Limit: the workflow runtime deletes a finished workflow after 30 days (`workflow/admin.go:52`). The same announcement delivered again after that would notify again. Announcements are acknowledged within minutes, so this does not happen in practice.

### D4. No delete guard; a deleted Event ends its notices

The first step reads the Order. When an admin deletes the Event before that step, `Order.Get` returns NotFound and the workflow ends without sending. Once the first step has run, its result is stored by the workflow runtime and the deletion no longer matters. The gap is the time from the announcement to the first step, seconds while the consumer runs. Accepted with the user (2026-11-06) instead of a guard that would need a send-time column or a query into the workflow runtime's tables.

### D5. Messages and links

- Emails go through the Postmark mailer the Order already uses for `SendConfirmationEmail`; `SendCancellationEmail` and `SendRefundEmail` are new methods on the same mailer interface and record nothing on the Order. Language follows `emailLanguage`, as in `SendResaleSold`.
- The ticket count and price in the cancellation email use the same rule as `Refund` (`unresoldAmount`): the Order's amount divided by its ticket count, times its Issued Tickets. The refund email uses the stored amount.
- The `event_cancelled` push opens the event page (`concertDeepLink`, `/events/<id>` for a first-party Event, which shows the 中止 banner). The `order_refunded` push opens `/orders/<order id>`, which shows the refunded banner.
- Notification types `event_cancelled` and `order_refunded` are added to `entity/notification.go` and the `notifications.type` column comment.

### D6. Durable consumers

Two NACK Consumer manifests in cloud-provisioning `k8s/namespaces/nats/base/jetstream/`: `send-event-cancelled` (stream `CONCERT`, filter `CONCERT.cancelled`) and `send-order-refunded` (stream `ORDER`, filter `ORDER.refunded`), registered in `internal/di/consumer.go`. They are applied before the backend release, because the backend binds only to declared durables.

## Risks / Trade-offs

- [Delete within seconds of a refund or a cancellation loses that notice] → D4; the admin sees the refund progress on the Artist concerts screen before deleting.
- [A refund record without its Refunded Order, or the reverse] → One writer in one transaction (D1), and contract tests that read both tables.
- [Existing Refunded Orders in production have no reason, amount or time] → Migration Plan step 1 counts them first.
- [The migration drops `orders.provider_refund_id` while old pods still read it] → Old pods fail reads of Orders between the migration and the rollout. Accepted: the product has no users yet, and the rollout follows the AtlasMigration within minutes.

## Migration Plan

1. Read-only in prod before the release: count Refunded Orders (`SELECT count(*) FROM orders WHERE status = 2`). When it is 0, the migration needs no backfill. When it is above 0, stop, record the count here, and decide the backfill with the user (reason and time are not stored anywhere today).
2. cloud-provisioning: merge the two Consumer manifests and confirm they are Ready.
3. backend: the Atlas migration creates `order_refunds`, copies `provider_refund_id` of any Refunded Order per step 1, and drops `orders.provider_refund_id`; release; confirm the AtlasMigration and the rollout.
4. Rollback: revert the backend release and add a migration that restores `orders.provider_refund_id` from `order_refunds`.
