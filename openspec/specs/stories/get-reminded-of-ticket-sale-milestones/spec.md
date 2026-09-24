# Get reminded of ticket sale milestones

## Purpose

A fan tracking a tour is reminded when a sales phase opens, 24 hours and 1 hour before it closes, and on the lottery result day, once per milestone and never between 22:00 and 08:00 in their time zone.

## Requirements

### Requirement: Milestone reminders reach tracking fans

For each known sales phase of a series, SalesReminderUseCase.ScanDueReminders SHALL find the milestones that have become due for each fan whose ticket journey on an event of the series is Tracking, and SalesReminderDeliveryUseCase.DeliverReminder SHALL deliver each of them, so the fan receives one push per milestone on each registered browser within 15 minutes of the milestone, outside the fan's quiet hours, and has one sales reminder Notification recorded for it.

#### Scenario: Sales open

- **WHEN** a tracked tour's presale opens at 12:00 in the fan's time zone
- **THEN** by 12:15 the fan's browser receives one Ticket Sales Open push naming the sales channel and the opening time

#### Scenario: Closing soon

- **WHEN** a tracked tour's presale closes at 20:00
- **THEN** the fan receives one reminder around 20:00 the day before and one around 19:00 that day

#### Scenario: Fan who has applied

- **WHEN** a fan sets their journey on the tour's event to Applied before the presale closes
- **THEN** the fan receives no closing reminders for it

### Requirement: No reminder at night

A milestone that falls between 22:00 and 08:00 in the fan's time zone SHALL be reminded at 08:00, or, for a closing reminder whose deadline comes before 08:00, before 22:00 the evening before.

Known defect: liverty-music/backend#472

#### Scenario: Opening at 02:00

- **WHEN** a tracked presale opens at 02:00 in the fan's time zone
- **THEN** the fan's Ticket Sales Open push arrives at about 08:00

### Requirement: Each milestone is reminded once

A reminder already delivered SHALL NOT be pushed again on a later scan. A fan with no registered browser SHALL receive nothing, and the reminder SHALL NOT be attempted again.

#### Scenario: Next scan

- **WHEN** the Ticket Sales Open reminder was delivered and the scan runs again 15 minutes later
- **THEN** the fan receives no second Ticket Sales Open push for that presale

#### Scenario: No registered browser

- **WHEN** a tracking fan has no registered browser when a presale opens
- **THEN** nothing is pushed and the reminder is not attempted again when the fan registers a browser later
