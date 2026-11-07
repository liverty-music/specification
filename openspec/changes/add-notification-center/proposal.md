## Why

A fan cannot see a notification again once the operating system drops it, and many notifications never reach the fan at all: in production, 52 of the 101 recorded notifications failed, 51 of them because the fan had no registered browser. The backend already records every notification, but nothing shows the record to the fan. The push messages are also inconsistent: only new_concerts names the artist, the concert appears in a different place in each type, resale pushes do not name the concert, and a fan with no preferred language gets English for some types and Japanese for others.

## What Changes

- Add a notification center to the fan web app: a list of the fan's 50 newest notifications, newest first, including those whose push failed. A bell in the page header shows the number of unread ones. Tapping an item marks it read and opens its link; opening a push notification from the operating system marks it read too.
- Add `NotificationService.List`. The server renders each notification's title, body and link when it lists it, with the same rendering the push uses, in the fan's current language.
- **BREAKING** A Notification stores what it is about (the ids of its artist, events, ticket sale, order or entry, and the reminder stage), not the rendered message. The title, body, link and tag are rendered from those records each time. `notifications.payload` is replaced by `subject`.
- **BREAKING** A Notification no longer records its delivery outcome. `delivery_status`, `failure_reason` and `delivered_at` are removed, together with Notification.UpdateDelivery, the `NOTIFICATION.delivered` announcement and the `notification.delivered` analytics event. NotificationUseCase.Deliver still returns the outcome to its caller and still logs it for analytics. `queued_at` becomes `created_at`.
- **BREAKING** Remove `NotificationService.Dismiss`, Notification.MarkDismissed and `dismissed_at`. The frontend never called them; a dismissed push is still reported to usage analytics by the Service Worker.
- Every push title reads `[<artist>] <headline>` and every body reads `<detail>` then a line break and the tour title. The artist is the notified artist for new_concerts and, for every other type, the performer the fan hypes highest. Notifications about a fan's tickets state the concert's date and venue in the body. New wording for every type in both languages.
- Stop the result-day reminder (`RESULT_DAY`) and the push for a first-come purchase. A won lottery is still pushed, as the new type `lottery_win` (replacing `order_confirmation`). Emails are unchanged.
- Rename the notification type `event_cancelled` to `concert_cancelled`, matching `CONCERT.cancelled`.
- **BREAKING** `UserService.Create` requires a preferred language, and a User always has one. The client no longer backfills a missing language on launch.

## Capabilities

### New Capabilities

- `components/entity/notification/list-by-user`: returns a fan's newest Notifications, newest first, up to a limit.
- `components/usecase/notification/list`: NotificationUseCase.List returns the caller's newest Notifications rendered in their language, with whether each is read.
- `components/infrastructure/fan/web/route/notifications`: the notification center screen.
- `stories/review-received-notifications`: a fan sees every notification sent to them, whether or not the push arrived, and which ones they have not read.

### Modified Capabilities

- `components/entity/notification`: (Purpose) the attributes become id, user, type, subject, create time and read time; the delivery states go. "A new Notification starts Queued", "The delivery outcome is consistent" and "Read and dismissed do not depend on delivery" are replaced by rules on the subject and the rendered message.
- `components/entity/notification/create`: stores the type and subject, not a message or a delivery status.
- `components/entity/notification/get`: returns the read time, not the delivery status or dismiss time.
- `components/entity/notification/update-delivery`: every requirement removed; the capability is retired.
- `components/entity/notification/mark-dismissed`: every requirement removed; the capability is retired.
- `components/entity/notification/mark-read`: unchanged; NotificationUseCase.MarkRead and List rely on it as it is.
- `components/usecase/notification/deliver`: records the type and subject, renders the message from them, and returns the outcome without storing it.
- `components/usecase/notification/dismiss`: every requirement removed; the capability is retired.
- `components/usecase/notification/notify-new-concerts`: the message wording and the subject it records.
- `components/usecase/notification/send-order-confirmation`: pushes only for a won lottery entry, as `lottery_win`.
- `components/usecase/notification/send-event-cancelled`: the push type becomes `concert_cancelled`, with the Order as its subject.
- `components/usecase/notification/send-lottery-loss`, `send-resale-entry-ended`, `send-order-refunded`: unchanged; they start Deliver with their type, named after the entry or Order, and the wording they describe is now rendered by the Notification entity.
- `components/usecase/ticket-sale/announce-discovered-sale`, `components/usecase/ticket-sale/scan-due-reminders`: the wording, and no `RESULT_DAY` reminder.
- `components/entity/ticket-sale-reminder`: (Purpose) the stage set loses `RESULT_DAY`; its requirements follow.
- `components/entity/ticket-sale/list-with-pending-milestones`: a sale is no longer kept listed for its result date.
- `components/entity/ticket-journey/list-user-ids-applied-series`: every requirement removed (only the result-day reminder used it); the capability is retired.
- `components/usecase/ticket-sale-reminder/deliver-reminder`: takes the fan's linked event instead of prepared content; it reads the outcome NotificationUseCase.Deliver returns, which keeps the same values.
- `components/adapter/fan/api/rpc/notification`: adds List; Dismiss is removed.
- `components/entity/user`: (Purpose) preferred language becomes required. "Absent preferred language is stored absent" in `components/entity/user/create` is removed.
- `components/usecase/user/create`, `components/adapter/fan/api/rpc/user`: Create requires a preferred language.
- `components/infrastructure/fan/web/global/page-header`: the bell with the unread count.
- `components/infrastructure/fan/web/global/service-worker`: opening a push notification marks it read.
- `stories/get-notified-of-new-concerts`: messages titled `[<artist>] …`; outcomes are no longer stored on the Notification.
- `stories/get-reminded-of-ticket-sale-milestones`: no result-day reminder; the new titles.
- `stories/hear-about-a-new-ticket-sale`: the new title; a fan without a browser finds the announcement in the notification center.
- `stories/restore-session-on-cold-start`: no language backfill.
- `components/infrastructure/fan/web/global/i18n`: "Backfill Preferred Language When Missing" is removed, and "Unified Language Preference Resolution" no longer handles a missing language.

## Impact

- **specification**: `proto/liverty_music/entity/v1/notification.proto` (`NotificationType`: `EVENT_CANCELLED` is renamed `CONCERT_CANCELLED`, `LOTTERY_WIN` is added, `ORDER_CONFIRMATION` is reserved; `Notification` loses `delivery_status`, `failure_reason`, `deliver_time` and `dismiss_time`, `queue_time` becomes `create_time`, and `message` carries the message rendered when it is listed), `rpc/notification/v1/notification_service.proto` (`List` added, `Dismiss` removed), `rpc/user/v1/user_service.proto` (`CreateRequest.preferred_language` required). Released before the downstream work, with the `buf skip breaking` label.
- **backend**: the `notifications` and `users` tables (migration), `ticket_sale_reminders` rows of `RESULT_DAY` (deleted), the Notification entity and repository, NotificationUseCase, the deliver workflow input, every push sender, the ticket-sale reminder scan, the analytics consumer, the notification and user handlers.
- **frontend**: a new `/notifications` route, the bell in the shell header, the Service Worker's notificationclick, the removal of the language backfill.
- **Data**: production has 101 notifications and 9 users (none without a language); existing notification rows are deleted by the migration.
