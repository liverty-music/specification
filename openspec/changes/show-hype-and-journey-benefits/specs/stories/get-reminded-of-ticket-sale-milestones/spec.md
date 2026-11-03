## RENAMED Requirements

- FROM: `### Requirement: Milestone reminders by method reach tracking fans`
- TO: `### Requirement: Milestone reminders reach tracking and applied fans`

## MODIFIED Requirements

### Requirement: Milestone reminders reach tracking and applied fans

For each known TicketSale of a series, discovered or the Organizer's own, TicketSaleReminderUseCase.ScanDueReminders SHALL find the milestones that have become due for each fan in the milestone's audience, and TicketSaleReminderDeliveryUseCase.DeliverReminder SHALL deliver each of them. The fan SHALL receive one push per milestone on each registered browser within 15 minutes of the milestone, outside the fan's quiet hours, and SHALL have one sales reminder Notification recorded for it. The milestones and their audiences are:

- for a first-come sale: 30 minutes before it opens, to each fan whose journey on an event of the series is Tracking
- for a lottery: when it opens and 24 hours before it closes, to each fan whose journey on an event of the series is Tracking
- for a discovered lottery whose pages state the day its results are announced: at 09:00 on that day, to each fan whose journey on an event of the series is Applied

Tapping a reminder SHALL open the detail sheet of the fan's earliest upcoming event of the series in that audience.

#### Scenario: First-come sale about to open
- **WHEN** a tracked tour's first-come sale opens at 19:00 in the fan's time zone
- **THEN** by 18:45 the fan's browser receives one まもなく先着販売開始 push naming the opening time and the tour

#### Scenario: Lottery reminders
- **WHEN** a tracked tour's discovered lottery opens on 5 October 18:00 and closes on 22 October 23:59
- **THEN** the fan receives one push around 5 October 18:00 and one around 08:00 on 22 October

#### Scenario: Fan who has applied
- **WHEN** a fan sets their journey on the tour's event to Applied before the lottery closes, and the lottery's page states that results are announced on 3 November 15:00
- **THEN** the fan receives no closing reminder for it, and receives one 今日は抽選結果の発表日 push around 09:00 on 3 November

#### Scenario: Result day not stated
- **WHEN** a fan's journey on the tour's event is Applied and the lottery's page does not state a result day
- **THEN** the fan receives no result-day push

#### Scenario: Fan still tracking on the result day
- **WHEN** a fan's journey on the tour's event is still Tracking on the lottery's result day
- **THEN** the fan receives no result-day push
