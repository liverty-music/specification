## Why

`move-decisions-into-entities` (archived 2026-11-16) moved the "is this email still due" decision of the lottery loss, resale sold and resale ended emails out of the Postmark senders: the entity decides (`LotteryEntry.LossEmailDue`, `ResaleListing.SoldEmailDue`, `ResaleEntry.EndedEmailDue`), the usecase records the send, and the sender only sends. The purchase confirmation email was left out. `PostmarkOrderMailer.SendConfirmationEmail` (`internal/infrastructure/mail/postmark.go:101`) still reads the Order again, returns without sending when `ConfirmationSendTime` is set, and records the send with `MarkConfirmationSent`. The same rule now has two homes in the same package family, the sender needs an `OrderStore` only for this, and `/opsx:verify` of that change reported it as the one place the principle still did not hold.

## What Changes

- `Order` gains `ConfirmationEmailDue`: the purchase confirmation is still to be sent. The Order's payment was captured and no confirmation has been sent.
- `NotificationUseCase.SendOrderConfirmation` sends the confirmation only while it is due, then records the send with `OrderRepository.MarkConfirmationSent`, in the order the loss, sold and ended emails already use (due, send, record).
- `PostmarkOrderMailer.SendConfirmationEmail` only sends. The mailer no longer reads or records an Order, so `mail.OrderStore` is removed and the mailer is built without a repository (`internal/di/consumer.go`, `internal/di/worker.go`). `SendCancellationEmail` and `SendRefundEmail` already send without deciding or recording and are unchanged.
- The `entity.OrderMailer.SendConfirmationEmail` contract changes from "sends once and records" to "sends as given"; it no longer fails with NotFound, because it no longer looks the Order up.
- The tests of the moved rule move with it: the "Redelivered event" case of the Postmark mailer test becomes an entity table test of `ConfirmationEmailDue` and a usecase test; the fake `OrderStore` of the mail tests is deleted.
- The tests `TestRunLotteryDraw*` of `internal/entity/lottery_draw_test.go` are renamed after what they exercise (`ShuffleDrawOrder` and `AdmitInDrawOrder`, through the test helper `runLotteryDraw`). `RunLotteryDraw` was deleted by the earlier change and only the names and comments of these tests still carry it.

No client-observable behaviour changes: the same Orders get one confirmation email and the same errors reach the caller, except that `SendConfirmationEmail` no longer reports NotFound for an unknown Order (the usecase reads the Order first and fails with NotFound itself).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `entity/order/send-confirmation-email`: the requirement "One confirmation email per order" is removed. The sender no longer decides whether the email is due or records that it was sent; a new requirement states that it sends the message as given, as `entity/lottery-entry/send-loss-email`, `entity/resale-listing/send-sold-email` and `entity/resale-entry/send-ended-email` now do.
- `usecase/notification/send-order-confirmation`: the requirement "Confirmation email after every paid Order" states that the usecase sends the email only while none has been sent (`Order.ConfirmationEmailDue`) and then records the send (`Order.MarkConfirmationSent`); its sequence diagram shows the due check, the send and the record.

`entity/order` is unchanged: the attribute `confirmation send time` already means "when the confirmation email was sent, empty until sent, set once". The entity operations the usecase relies on are `Order.Get` (unchanged), `Order.SendConfirmationEmail` (sends as given) and `Order.MarkConfirmationSent` (unchanged, a compare-and-set that keeps the first time); `Order.ConfirmationEmailDue` is a predicate stated in the usecase requirement, as `LossEmailDue` is in `send-lottery-loss`.

## Impact

- Backend only: `internal/entity/order.go` (the predicate and the `OrderMailer` and `OrderRepository` doc comments), `internal/usecase/order_confirmation.go`, `internal/infrastructure/mail/postmark.go` (the mailer and `OrderStore`), `internal/di/consumer.go` and `internal/di/worker.go` (construction of the mailer), the mocks of `OrderMailer`, and the tests named above.
- Specification: the two delta specs; the Purpose of `entity/order/send-confirmation-email` and the diagram of `usecase/notification/send-order-confirmation` are edited in the main specs at archive time, as for the earlier change (Purposes are never edited through a delta).
- No API, proto, schema or migration change; `MarkConfirmationSent` and its SQL are unchanged.
