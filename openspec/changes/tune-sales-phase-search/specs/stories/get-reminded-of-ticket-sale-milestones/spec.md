# Spec Delta

## ADDED Requirements

### Requirement: Milestone reminders by method reach tracking fans

For each known sales phase of a series, SalesReminderUseCase.ScanDueReminders SHALL find the milestones that have become due for each fan whose ticket journey on an event of the series is Tracking, and SalesReminderDeliveryUseCase.DeliverReminder SHALL deliver each of them. The fan SHALL receive one push per milestone on each registered browser within 15 minutes of the milestone, outside the fan's quiet hours, and SHALL have one sales reminder Notification recorded for it. The milestones are:

- for a first-come sale: 30 minutes before it opens
- for a lottery: when it opens, 24 hours before it closes, and on the result day

Tapping a reminder SHALL open the detail sheet of the fan's earliest upcoming tracked event of the series.

#### Scenario: First-come sale about to open

- **WHEN** a tracked tour's first-come sale opens at 19:00 in the fan's time zone
- **THEN** by 18:45 the fan's browser receives one まもなく先着販売開始 push naming the opening time and the tour

#### Scenario: Lottery reminders

- **WHEN** a tracked tour's lottery opens on 5 October 18:00, closes on 22 October 23:59 and announces results on 3 November 15:00
- **THEN** the fan receives one push around 5 October 18:00, one around 08:00 on 22 October, and one around 09:00 on 3 November

#### Scenario: Fan who has applied

- **WHEN** a fan sets their journey on the tour's event to Applied before the lottery closes
- **THEN** the fan receives no closing reminder for it

### Requirement: No reminder at night, and first-come reminders come earlier

A milestone that falls between 22:00 and 08:00 in the fan's time zone SHALL be reminded at 08:00. The exception is a first-come sale's reminder, which SHALL arrive at 21:00 the evening before, so it still comes before the sale opens.

#### Scenario: Lottery opening at 02:00

- **WHEN** a tracked lottery opens at 02:00 in the fan's time zone
- **THEN** the fan's チケット申し込み受付開始 push arrives at about 08:00

#### Scenario: First-come sale at midnight

- **WHEN** a tracked first-come sale opens at 00:00 in the fan's time zone
- **THEN** the fan's まもなく先着販売開始 push arrives at about 21:00 the evening before

## REMOVED Requirements

### Requirement: Milestone reminders reach tracking fans

**Reason**: The milestones reminded now depend on the method.
**Migration**: Replaced by "Milestone reminders by method reach tracking fans".

### Requirement: No reminder at night

**Reason**: The close-stage 21:00 rule is replaced by moving a first-come reminder earlier.
**Migration**: Replaced by "No reminder at night, and first-come reminders come earlier".
