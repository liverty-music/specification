# Spec Delta

## MODIFIED Requirements

### Requirement: Milestone reminders by method reach tracking fans

For each known TicketSale of a series, discovered or the Organizer's own, TicketSaleReminderUseCase.ScanDueReminders SHALL find the milestones that have become due for each fan whose ticket journey on an event of the series is Tracking, and TicketSaleReminderDeliveryUseCase.DeliverReminder SHALL deliver each of them. The fan SHALL receive one push per milestone on each registered browser within 15 minutes of the milestone, outside the fan's quiet hours, and SHALL have one sales reminder Notification recorded for it. The milestones are:

- for a first-come sale: 30 minutes before it opens
- for a lottery: when it opens, 24 hours before it closes, and on the result day

Tapping a reminder SHALL open the detail sheet of the fan's earliest upcoming tracked event of the series.

#### Scenario: First-come sale about to open
- **WHEN** a tracked tour's first-come sale opens at 19:00 in the fan's time zone
- **THEN** by 18:45 the fan's browser receives one まもなく先着販売開始 push naming the opening time and the tour

#### Scenario: Lottery reminders
- **WHEN** a tracked tour's discovered lottery opens on 5 October 18:00, closes on 22 October 23:59 and announces results on 3 November 15:00
- **THEN** the fan receives one push around 5 October 18:00, one around 08:00 on 22 October, and one around 09:00 on 3 November

#### Scenario: Fan who has applied
- **WHEN** a fan sets their journey on the tour's event to Applied before the lottery closes
- **THEN** the fan receives no closing reminder for it

## ADDED Requirements

### Requirement: The Organizer's own sales are reminded too

A fan tracking an event of an Organizer's Published Series SHALL receive the same milestone reminders for each of the Organizer's TicketSales that offers that event as for discovered sales, and none for a sale that does not offer an event the fan tracks. Tapping such a reminder SHALL open the detail sheet of the fan's earliest upcoming tracked event that the sale offers. The result day of the Organizer's lottery SHALL be the day it closes, because its draw runs within 1 minute after it closes. A fan SHALL receive no reminder for a sale of a Series that is Cancelled.

#### Scenario: Organizer's lottery reminders
- **WHEN** a fan tracks an event of an Organizer's Published Series whose lottery opens on 5 October 18:00 and closes on 12 October 23:59
- **THEN** the fan receives one チケット申し込み受付開始 push around 5 October 18:00, one 抽選の申し込み締切が近づいています push around 08:00 on 12 October, and one 本日 抽選結果発表 push around 09:00 on 12 October

#### Scenario: Organizer's first-come sale
- **WHEN** a fan tracks an event of an Organizer's Published Series whose first-come sale opens on 6 October 19:00
- **THEN** by 18:45 on 6 October the fan's browser receives one まもなく先着販売開始 push

#### Scenario: Sale for another event of the tour
- **WHEN** a fan tracks only the Osaka event of an Organizer's tour and the Organizer's lottery offers only the Tokyo event
- **THEN** the fan receives no reminder for that lottery

#### Scenario: Series cancelled before the sale opens
- **WHEN** an Organizer cancels the Series the day before its lottery opens
- **THEN** the tracking fan receives no reminder for that lottery
