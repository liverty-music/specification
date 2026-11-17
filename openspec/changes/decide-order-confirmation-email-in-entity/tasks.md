## 1. backend: the decision and the record (components/entity/order, components/usecase/notification/send-order-confirmation)

Sections 1 to 3 are one backend PR; the commit hook and CI run `make check` on it.

- [ ] 1.1 Add `Order.ConfirmationEmailDue` in `internal/entity/order.go` (design.md "`Order.ConfirmationEmailDue` is paid and not yet confirmed": `PayTime != nil && ConfirmationSendTime == nil`), with a doc comment in the form of `LossEmailDue`'s. Verify with an entity table test over a Paid Order without and with a send time, a Refunded Order without one (still due), and a Pending and a Void Order (never due)
- [ ] 1.2 Change `SendOrderConfirmation` (`internal/usecase/order_confirmation.go`) to send only while `order.ConfirmationEmailDue()` and then call `d.Orders.MarkConfirmationSent(ctx, order.ID, d.Now())`, in the order `lottery_loss.go` uses; leave the push step as it is. Verify with usecase tests that use the `OrderMailer` and `OrderRepository` mocks, one per scenario of `usecase/notification/send-order-confirmation` in the requirement "Confirmation email after every paid Order" ("Checkout paid", "Lottery win", "Order announced twice": no send and no record, and the push still started; "Mail unavailable": no record), annotated with `@spec`; `order_confirmation_test.go` drops the cases that re-checked the send-once rule

## 2. backend: the mailer only sends (components/entity/order/send-confirmation-email)

- [ ] 2.1 Make `PostmarkOrderMailer.SendConfirmationEmail` (`internal/infrastructure/mail/postmark.go`) validate the address and message and post the email, and nothing else. Delete `mail.OrderStore`, the `orders` and `clock` fields and the matching arguments of `NewPostmarkOrderMailer`, update `provideNotificationMailers` (`internal/di/consumer.go`) and the mailer's construction in `internal/di/worker.go`, and reword the doc of `entity.OrderMailer.SendConfirmationEmail` (sends as given; InvalidArgument and Unavailable only). Verify with `postmark_test.go`: the cases "Email sent" and "Mail unavailable" carry `@spec components/entity/order/send-confirmation-email` annotations of the new requirement "The confirmation email is sent as given", the case "Redelivered event", the NotFound case and `fakeOrders` are gone, and the cancellation, refund, black-hole domain, empty address and message and test-server-token cases still pass unchanged
- [ ] 2.2 Check that nothing in `internal/infrastructure/mail` decides or records any more. Verify that `git grep -nE "OrderStore|ConfirmationSendTime|MarkConfirmationSent" -- internal/infrastructure/mail` prints nothing

## 3. backend: the lottery draw tests name what they test (components/entity/lottery-entry/run-lottery-draw)

- [ ] 3.1 Rename `TestRunLotteryDraw` and `TestRunLotteryDraw_*` in `internal/entity/lottery_draw_test.go` to `TestLotteryDraw` and `TestLotteryDraw_*`, and reword their comments to say that the helper `runLotteryDraw` shuffles with `ShuffleDrawOrder` and admits with `AdmitInDrawOrder`; keep the `@spec` annotations. Verify that `git grep -n "RunLotteryDraw" -- internal` prints nothing and that the annotated scenarios of `run-lottery-draw` are still found by `scripts/check-scenario-coverage.py` in the store

## 4. production check after the release

- [ ] 4.1 After the release that holds section 1 to 3, read the rollout and the first minutes of `event-consumer` and `workflow-worker` in production with the `liverty-music` gcloud configuration. Verify that both Deployments run the new tag with no restart and that the first 15 minutes of their logs hold no ERROR other than the start-up connection retries of `workflow-worker`; when an `ORDER.paid` announcement is delivered in that window, verify in the `event-consumer` log that its confirmation email was sent once

## 5. specification: close out

- [ ] 5.1 After the backend PR is merged and released, run `/opsx:verify` and archive in a `<change>-archive` worktree (README "Lifecycle of a change", step 5). In the same PR edit the main specs the archive leaves behind: the Purpose of `entity/order/send-confirmation-email` (the sender sends as given; the caller decides whether the email is due and records the send, so it is sent once per Order) and the Purpose sequence diagram of `usecase/notification/send-order-confirmation` (show `Order.ConfirmationEmailDue`, `Order.SendConfirmationEmail` and `Order.MarkConfirmationSent` in that order). Verify that the archive PR's `openspec-checks` job passes, which runs `scripts/check-diagrams.py` and `scripts/check-scenario-coverage.py`
