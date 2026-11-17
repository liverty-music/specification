## Context

`move-decisions-into-entities` settled the shape for an email that must be sent once (see its archived `design.md`, "Rules and their homes"): the entity predicate says the email is due, the usecase reads, asks the entity, sends through the mail port and then records, and the mail package only sends. Three emails follow it today:

| Email | Predicate | Record | Usecase |
|---|---|---|---|
| Lottery loss | `LotteryEntry.LossEmailDue` | `LotteryEntryRepository.MarkLossEmailSent` | `usecase/lottery_loss.go` |
| Resale sold | `ResaleListing.SoldEmailDue` | `ResaleListingRepository.MarkSoldEmailSent` | `usecase/resale_sold.go` |
| Resale ended | `ResaleEntry.EndedEmailDue` | `ResaleEntryRepository.MarkEndedEmailSent` | `usecase/resale_entry_ended.go` |

The purchase confirmation still has the old shape. `PostmarkOrderMailer.SendConfirmationEmail` reads the Order through `mail.OrderStore`, returns when `ConfirmationSendTime` is set, posts the email and calls `MarkConfirmationSent`. `OrderRepository.MarkConfirmationSent` already is the compare-and-set the usecase needs (`UPDATE orders SET confirmation_send_at = $2 WHERE id = $1 AND confirmation_send_at IS NULL`, NotFound when no Order has the id), so no repository change is needed. The mailer is built in two processes: the event consumer (`internal/di/consumer.go`, `provideNotificationMailers`) and the workflow worker (`internal/di/worker.go`); the worker uses it only for the cancellation and refund notices, which already send without deciding or recording.

## Goals / Non-Goals

**Goals:**

- The confirmation email has the same three-part shape as the other three: an `Order` predicate, the usecase recording the send, the mailer only sending.
- `mail` no longer depends on the Order repository.

**Non-Goals:**

- The cancellation and refund notices. They record nothing, so there is no decision to move; whether they should be sent once is a question about their own behaviour and not part of this change.
- Making the send and the record atomic. They are two steps today and stay two steps (see Risks).
- Any change to the email content, the push notification or the announcement that triggers the usecase.

## Decisions

### `Order.ConfirmationEmailDue` is "paid and not yet confirmed"

`func (o *Order) ConfirmationEmailDue() bool` returns `o.PayTime != nil && o.ConfirmationSendTime == nil`. `PayTime` is set when the payment is captured (the Paid transition in `entity/order.go`; the column `pay_at` is written only by `issuance_repo.go:42`) and nothing clears it, so a Paid Order and one that was Refunded afterwards both have it.

Alternatives: `ConfirmationSendTime == nil` alone keeps the adapter's condition word for word, but then the predicate says nothing a caller could not read off the field, and a confirmation could go out for a Pending or Void Order that was passed to the usecase by mistake. `Status == OrderStatusPaid` would skip an Order that was Refunded between the `ORDER.paid` announcement and the consumer's run, which today still gets its confirmation; that is a behaviour change this change does not make. `PayTime != nil` keeps every Order that was announced as paid and rejects the ones that never were.

### The usecase decides, sends, records

`SendOrderConfirmation` keeps its reads. After building the content it does what `lottery_loss.go` does: when `order.ConfirmationEmailDue()`, it calls `Mailer.SendConfirmationEmail` and then `Orders.MarkConfirmationSent(ctx, order.ID, d.Now())`; otherwise it sends nothing. The push notification step is unchanged and still runs on a repeated announcement, where its workflow id keeps it to one push. `d.Orders` is already an `entity.OrderRepository`, which declares `MarkConfirmationSent`; no new dependency is added to `OrderConfirmationDeps`.

### The mailer takes the Order's id and sends

`PostmarkOrderMailer.SendConfirmationEmail` validates the address and the message (InvalidArgument), posts the email tagged `orderConfirmationTag` with the Order's id in the metadata, and returns. `mail.OrderStore`, the `orders` and `clock` fields of `PostmarkOrderMailer` and the matching constructor arguments are deleted; `NewPostmarkOrderMailer(serverToken, fromAddress, messageStream, logger)` and its two call sites follow. `provideNotificationMailers` loses its `orders` parameter and `worker.go` its `orderRepo` argument. `entity.OrderMailer` stays one interface of three methods; only the doc of `SendConfirmationEmail` changes (it sends as given, no NotFound). Splitting it into one interface per email, as the earlier change did for emails that had a single method, would add three types for no consumer that needs them.

### Tests move with the rule

- `Order.ConfirmationEmailDue`: an entity table test over status and `PayTime` and `ConfirmationSendTime` (paid and unsent; sent; refunded and unsent; pending; void).
- `SendOrderConfirmation`: usecase tests with the `OrderMailer` and `OrderRepository` mocks, one per scenario of the usecase spec: send then record in that order, no send and no record when a confirmation was already sent ("Order announced twice"), no record when the send fails ("Mail unavailable"), and the push still started after a repeated announcement.
- The Postmark mailer test keeps the send, the black-hole domain, the empty address and message cases and the test server token case, and drops "Redelivered event", `fakeOrders` and the NotFound case. Its `@spec` annotations for the confirmation email follow the scenarios of the new requirement ("Email sent", "Mail unavailable").
- `TestRunLotteryDraw*` in `internal/entity/lottery_draw_test.go` are renamed to `TestLotteryDraw*`, and their comments say that the helper `runLotteryDraw` shuffles with `ShuffleDrawOrder` and admits with `AdmitInDrawOrder`. The `@spec` annotations of `run-lottery-draw` stay as they are.

## Risks / Trade-offs

- [A failure between the send and the record sends a second email on retry] → Unchanged: today the mailer has the same window between its post and `MarkConfirmationSent`. The spec already says so ("a failure between sending and recording can lead to a second email on retry"); the usecase requirement keeps that sentence's meaning ("a run again after the email was sent sends no second email").
- [Two runs for one announcement overlapping each read the Order before either records] → Unchanged: the adapter also read, sent and then recorded, with no lock between the read and the record. `MarkConfirmationSent` keeps the first time, so the Order ends with one send time. No row lock is added, because this is not a check-then-write that creates or deletes records; the worst case is the duplicate email already accepted above.
- [The mailer no longer returns NotFound for an unknown Order] → The usecase reads the Order first with `Order.Get`, which fails with NotFound before any send, so the usecase's observable errors are the same.

## Migration Plan

Code only; no data or API change. The backend deploys as a normal release and is rolled back by reverting its PR. Order of work: the `Order` predicate and the usecase first (the usecase then records while the mailer still records, and `MarkConfirmationSent` keeps the first time, so a mixed state is harmless), then the mailer and its wiring.
