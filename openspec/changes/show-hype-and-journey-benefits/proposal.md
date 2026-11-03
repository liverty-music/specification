## Why

Fans do not set hype levels or ticket journeys because nothing tells them what either one gets them. A hype level decides which new concerts reach the fan by push, but only the My Artists help sheet says so, and a fan does not see a push that never came. Tracking an event is what turns on ticket sale reminders, but the event detail sheet shows it as one of five record-keeping buttons labelled 「追跡中」. This change says, in the fan's words and at the moment of choice, what each value delivers by push, and fixes the reminder and sign-up specs that describe behaviour the app does not have (issue #1321).

## What Changes

- **My Artists, hype snack.** Changing a hype level shows one snack in the form 「ヨルシカの{全て|東京|東京周辺}の新着ライブをプッシュ通知します🔔」 (Watch: 「ヨルシカの新着ライブはプッシュ通知しません」). With push on, a level's snack appears the first time the fan picks that level on the device. With push off, it reads 「…をプッシュ通知で受け取ろう🔔」 with an action that turns push on, and appears every time. A guest sees the 「受け取ろう」 form with 「登録する」, the first time per level. The separate push-offer snack after a hype change goes; its offer is this snack's action.
- **Snack bar.** At most three snacks show at once in the fan app; a fourth dismisses the oldest snack that dismisses on its own. The app update snack is never dismissed by this and does not count.
- **Push offer.** The offer also appears in the hype snack every time push is off (no per-session cap, no stop after three unanswered offers), and next to the push promise in the ticket section. A fan whose browser blocked notifications, or cannot receive them, gets a link to Settings instead.
- **Event detail sheet, ticket section.** The section sits under the venue and holds the official site button. Its first control is one large button 「🔔 チケット販売の通知を受け取る」 (Tracking); pressed again it stops. The other four statuses stay one tap away in one row (📝 申込済み › 💰 当選・未入金 › 🎟️ 入金済み, 💔 落選); pressing the selected one clears it. One line under the controls says what reaches the fan by push for the current status. A guest sees the button; pressing it starts sign-up and the event is tracked once the account exists.
- **Tracking icon.** Tracking shows 🔔 instead of 👀 everywhere (card badge, filter chip, sheet), because 👀 is also the Watch hype level, which means no push.
- **Out-of-range notice.** On the sheet of a concert the fan's hype level does not match, a notice under the venue reads 「今は**東京周辺**の新着ライブだけプッシュ通知対象です」 with a button 「全ての新着ライブを受け取る」 (the lowest level that matches the concert, set by the fan).
- **Lottery result day.** Discovery reads a lottery's result announcement date when the pages state it. On that date, each fan whose journey on an event of the series is Applied gets one push. A fan who has not recorded Applied gets none.
- **Spec corrections.** `stories/get-reminded-of-ticket-sale-milestones` promises a result-day reminder to tracking fans that no code sends; it now states the Applied-fan reminder above. `stories/sign-up-or-sign-in` describes a Step 6 sign-up modal that does not exist; it now lists where sign-up actually starts.
- The two snacks that `infer-hype-and-journey` adds to the event detail sheet (calendar tracking, hype raise) take the wording above.

## Capabilities

### New Capabilities
- `components/entity/ticket-journey/list-user-ids-applied-series`: the fans whose journey on any event of a series is Applied, each with one linked event: the audience of a lottery's result-day reminder.

### Modified Capabilities
- `components/entity/ticket-sale` (Purpose): new attribute `result date`. Requirements: only a discovered Lottery sale has one, on or after the date of its end time.
- `components/entity/ticket-sale/search-published-sales`: returns a lottery's result date when the pages state it.
- `components/entity/ticket-sale/upsert-discovered`: stores and replaces the result date.
- `components/entity/ticket-sale/list-with-pending-milestones`: keeps a sale while its result date has not passed.
- `components/entity/ticket-sale-reminder` (Purpose): new stage `RESULT_DAY`. Requirements: the stage values and the stage anchored on the result date.
- `components/usecase/ticket-sale/scan-due-reminders`: `RESULT_DAY` for discovered lotteries with a result date, sent to Applied fans, with its content and expiry. It reads TicketJourney.ListUserIDsAppliedSeries (new); TicketSale.ListWithPendingMilestones changes as above; the other operations it calls are unchanged.
  `TicketSaleReminderDeliveryUseCase.DeliverReminder` is not changed: it delivers any stage the scan requests.
- `components/infrastructure/fan/web/route/my-artists`: the hype snack replaces the push offer after a hype change.
- `components/infrastructure/fan/web/global/snack-bar`: at most three snacks at once.
- `components/infrastructure/fan/web/global/notification-prompt`: where the push offer appears, who can use it, and no limits on the hype snack's offer.
- `components/infrastructure/fan/web/global/event-detail-sheet`: the ticket section's place, its controls, the push line, the guest button, the out-of-range notice, and the wording of the two snacks from `infer-hype-and-journey`.
- `components/infrastructure/fan/web/route/dashboard`: the ticket section's i18n keys, its layout, and the Tracking icon in the journey presentation map.
- `components/infrastructure/fan/web/global/page-help`: resetting onboarding also clears the hype snack's per-level flags.
- `stories/track-ticket-journey`: a guest's tracking button leads to sign-up and tracks the event after it.
- `stories/get-reminded-of-ticket-sale-milestones` (Purpose): the result-day reminder reaches Applied fans. Requirements: the milestones and who receives the result-day push.
- `stories/sign-up-or-sign-in`: the entry points of sign-up; no tutorial step.

**Built on `infer-hype-and-journey`**: the deltas of `event-detail-sheet` (its two snack requirements) and of `stories/sign-up-or-sign-in` ("Every sign-in resolves the account with Create") are written against the main specs as that change leaves them, and the out-of-range button stores the level as set by the fan, which that change introduces. That change is archived first.

## Impact

- **backend**: migration adding `ticket_sales.result_date DATE` (discovered lotteries only) and allowing stage 4 in `ticket_sale_reminders`; the ticket sale search prompt and response schema gain the result date; `TicketSale.UpsertDiscovered`, `TicketSale.ListWithPendingMilestones`, new `TicketJourney.ListUserIDsAppliedSeries`, `ReminderStage` `RESULT_DAY` and its content in `ScanDueReminders`.
- **frontend**: snack bar limit; My Artists hype snack and its per-level flags in device storage; push offer rules; event detail sheet ticket section, out-of-range notice and snack wording; Tracking icon; guest tracking intent carried through sign-up; i18n keys.
- **specification**: no proto change. A discovered TicketSale is not a proto message, and `ReminderStage` is not in proto.
- **cloud-provisioning**: none.
- **Follow-ups**: notifying the losers of an Organizer's lottery (today only the winners get an email); a result date that a page publishes only after the sale has opened is not picked up, because discovery no longer searches a series whose sale is under way.
