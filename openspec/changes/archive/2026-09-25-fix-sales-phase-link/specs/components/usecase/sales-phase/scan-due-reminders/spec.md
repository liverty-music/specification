# Scan Due Reminders Delta

## MODIFIED Requirements

### Requirement: Reminder content

Each requested reminder SHALL carry a title that names the stage, a text that names the sales channel and the stage's milestone time, a link and a grouping tag, in the fan's preferred language: Japanese for `ja` and English for any other or no language. The channel label SHALL be the phase's provider name when it has one, otherwise the channel's name, and a generic ticket label (チケット / Ticket) when the channel is not yet determined. The milestone time SHALL be shown as month, day and hour:minute in the fan's time zone. The link SHALL be the phase's url when it has one; otherwise the concert page of the series' earliest upcoming Event, or its earliest Event when none is upcoming; when the series has no Event it SHALL be the dashboard. Repeated deliveries of the same phase and stage SHALL replace each other on the device, and different stages SHALL NOT.

#### Scenario: Play-guide presale opens

- **WHEN** an `APPLY_OPEN` reminder is built in English for a phase with provider name イープラス opening on 1 July 10:00 in the fan's time zone
- **THEN** the title is Ticket Sales Open and the text is イープラス sales open at Jul 1 10:00

#### Scenario: Channel not determined

- **WHEN** a reminder is built in Japanese for a phase with no provider name and channel `UNSPECIFIED`
- **THEN** the text names the channel as チケット

#### Scenario: No application url

- **WHEN** the phase has no url
- **THEN** the reminder links to the concert page of the series' earliest upcoming Event

#### Scenario: No application url and no upcoming event

- **WHEN** the phase has no url and every Event of the series is in the past
- **THEN** the reminder links to the concert page of the series' earliest Event

#### Scenario: No application url and no event

- **WHEN** the phase has no url and the series has no Event
- **THEN** the reminder links to the dashboard
