## Why

When a member cancels (中止) a concert, the fans who bought tickets for it are told nothing: no email, no push. When an admin then refunds their Orders, they are told nothing either; the only signals are the event page, the order screen and the card statement (liverty-music/specification#1241). The pilot charges real money, and the Terms promise a refund only for 中止, so a fan must hear both that the concert is off and that the money came back.

A refund also leaves no record of why, how much or when it was made: `Order.CommitRefund` stores only the provider refund ID. The refund notice needs the amount, the dispute case must be told apart from 中止, and receipts and bookkeeping (`payments-legal-compliance` 3.1, 3.3) need all three.

## What Changes

- `Series.CancelEvents` announces each Event it makes CANCELLED, with the change.
- New `NotificationUseCase.SendEventCancelled`: for each Paid Order of a cancelled Event, an email and an `event_cancelled` push say the concert is cancelled and that the price of the tickets the fan still holds is refunded to the card they paid with. The push opens the event page.
- An Order records its refund: the reason (中止 or dispute), the amount refunded to the card and the time, together with the provider refund ID. `OrderUseCase.Refund` gives `Order.CommitRefund` the reason and the amount, and `CommitRefund` announces the Order as refunded once, with the change.
- New `NotificationUseCase.SendOrderRefunded`: for an Order refunded for 中止, an email and an `order_refunded` push give the amount, the card brand and last four digits, and say that the refunded tickets are no longer valid. The push opens the order. An Order refunded for a dispute is not notified: the card issuer returned the money, and `dispute-representment` will change that flow.
- Each notice is sent once per Order without a send-time record: its receiver runs it as a workflow named after the Order. An Event deleted before a notice reads its Order ends that notice without sending.
- New notification types `event_cancelled` and `order_refunded`.

## Capabilities

### New Capabilities

- `components/entity/order/send-cancellation-email`: emails the user of an Order that its concert is cancelled and its tickets are refunded.
- `components/entity/order/send-refund-email`: emails the user of a refunded Order the amount refunded and the card it went to.
- `components/usecase/notification/send-event-cancelled`: tells each fan with a Paid Order of a cancelled Event, by email and push.
- `components/usecase/notification/send-order-refunded`: tells the fan of an Order refunded for 中止, by email and push.

### Modified Capabilities

- `components/entity/series/cancel-events`: announces each Event it makes CANCELLED.
- `components/entity/order/commit-refund`: records the refund's reason, amount and time, and announces the refunded Order once.
- `components/usecase/order/refund`: gives the reason and the refunded amount to `Order.CommitRefund`.
- `components/usecase/notification/deliver`: also runs for `SendEventCancelled` and `SendOrderRefunded`.
- `stories/remove-a-cancelled-concert`: each fan is told of the cancellation and of the refund.
- `components/entity/order` (Purpose, edited by archive task 7.2): attributes refund reason, refund amount and refund time; the provider refund ID is present for a 中止 refund that moved money.
- `components/entity/notification` (Purpose, edited by archive task 7.2): types `event_cancelled` and `order_refunded`.

Unchanged and why: `components/usecase/series/cancel` already cancels through `Series.CancelEvents`, which now announces; `components/entity/order/get` and `list-by-event` return the Order with its attributes, the new ones included; `components/entity/concert/delete-and-suppress` already removes a Refunded Order with its records, and its refund record goes with it; `components/usecase/user/get` and `components/entity/concert/list-by-ids` are read as they are.

## Impact

- **backend**: `CancelEvents` announces `CONCERT.cancelled`; `Order.CommitRefund` stores the refund record and announces `ORDER.refunded`; a migration adds the `order_refunds` table and moves `orders.provider_refund_id` into it; `SendEventCancelled`, `SendOrderRefunded`, `Order.SendCancellationEmail`, `Order.SendRefundEmail`, their workflows and two durable consumers; notification types `event_cancelled`, `order_refunded`.
- **cloud-provisioning**: two NACK Consumer manifests, `send-event-cancelled` (`CONCERT.cancelled`) and `send-order-refunded` (`ORDER.refunded`), applied before the backend release.
- **specification (proto)**: `NotificationType` gains `NOTIFICATION_TYPE_EVENT_CANCELLED` and `NOTIFICATION_TYPE_ORDER_REFUNDED`, so the `NOTIFICATION.delivered` announcement of these notices names their type. `Order.provider_refund_id` keeps its field and meaning.
- **frontend**: none. The event page already says the concert is cancelled, and the order screen already says the Order is refunded.
- Analytics: no new event.
