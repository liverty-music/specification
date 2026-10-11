# Spec Delta

## ADDED Requirements

### Requirement: Opened from the event's Sales tab and back

The lottery sale editor SHALL be opened from 抽選で販売する on an event's Sales tab, SHALL show that event's date, start time and venue, and SHALL have the event as its parent in the breadcrumb. After the sale is created the console SHALL return to the event's Sales tab; leaving without saving SHALL return there too, guarding unsaved changes.

#### Scenario: Back after creating

- **WHEN** an operator creates a lottery sale from the Sales tab of the 3 November event
- **THEN** the Sales tab of the 3 November event opens and lists the new sale

#### Scenario: Breadcrumb

- **WHEN** the editor is open for the 3 November event of XX Tour 2026
- **THEN** the breadcrumb reads 公演 › XX Tour 2026 › 11月3日(火) › 抽選で販売

### Requirement: The window is entered in Japan time

The editor SHALL take the sale's start and end as Japan time, marked JST, whatever the device's time zone, and SHALL show the price with yen separators.

#### Scenario: Device in another time zone

- **WHEN** an operator whose device is set to London time enters a start of 2026-10-10 12:00 JST and saves
- **THEN** the sale opens at 12:00 Japan time on 10 October
