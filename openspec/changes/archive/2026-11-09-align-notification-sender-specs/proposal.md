## Why

`add-notification-center` moved every notification's text into the Notification entity: a sender names the notification's subject, and the entity renders the message from that subject's records in the fan's language. The review of its archive (specification#1362) found three places where the specs still disagree with that, or with the code on `backend` `main`:

- The entity's copy table has no row for a lottery loss whose lost reason is "concert cancelled", although the backend renders one (`copyLotteryCancelled` in `internal/entity/notification_message.go`) and the SendLotteryLoss scenario "Concert cancelled push" expects that text.
- SendLotteryLoss and SendOrderRefunded still describe the text they push ("saying ... that the entry lost", "saying ... that the price was refunded"), as if each sender wrote it. The entity's table now owns that text, so the same wording would live in two places.
- The Purpose of UserUseCase.Create says the preferred language is optional, while its requirements, since `add-notification-center`, require it.

The code already behaves as the corrected specs say; only the specs change.

## What Changes

- The Notification entity's copy table gains the row `lottery_loss, concert cancelled` with the text the backend renders.
- SendLotteryLoss and SendOrderRefunded say that the entity renders the pushed message from the subject, instead of describing its text.
- The Purpose of UserUseCase.Create says the preferred language is captured at sign-up and the home area is optional. A Purpose has no delta, so it is edited directly in the main spec.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/notification`: the copy table gains the lottery_loss row for a cancelled concert.
- `components/usecase/notification/send-lottery-loss`: the push requirement points to the entity's rendering instead of describing the text.
- `components/usecase/notification/send-order-refunded`: the refund notice requirement points to the entity's rendering instead of describing the push text.
- `components/usecase/user/create` (Purpose): the preferred language is required and the home area optional.

## Impact

Specs only. No code, API or data changes: `backend` `main` already renders the added row (`internal/entity/notification_message.go`, tested in `internal/entity/notification_message_test.go`) and already requires the preferred language at sign-up.
