## Purpose

Returns the fans whose ticket journey on any event of a series is Applied, each with one linked event, which is the audience of a discovered lottery's result-day reminder.

## ADDED Requirements

### Requirement: ListUserIDsAppliedSeries returns each applied fan once

ListUserIDsAppliedSeries SHALL return every fan who has a journey with status Applied on at least one event of the given series. Each fan SHALL appear once, however many events of the series they applied for. With each fan it SHALL return the fan's linked event, chosen among the events of the series whose journey is Applied as follows:

- the earliest upcoming event
- otherwise, the earliest event

An event is upcoming when its date is today or later. A fan whose journeys on the series are all in another status (Tracking, Lost, Unpaid, Paid) SHALL NOT be returned. The result has no particular order. It SHALL be empty when nobody has applied for any event of the series.

#### Scenario: Fans who applied for events of the series

- **WHEN** fan A's journeys on two events of the series are Applied and fan B's journey on one event is Applied
- **THEN** the result contains fan A once and fan B once

#### Scenario: Linked event is the earliest upcoming applied event

- **WHEN** fan A's journeys on the series' 1 November and 15 November events are Applied, and fan A's journey on its earlier 20 October event is Tracking
- **THEN** fan A's linked event is the 1 November event

#### Scenario: Every applied event is past

- **WHEN** fan A's only Applied journeys on the series are on its 1 September and 5 September events and both are past
- **THEN** fan A's linked event is the 1 September event

#### Scenario: A fan still tracking

- **WHEN** fan C's only journey on the series is Tracking
- **THEN** fan C is not in the result

#### Scenario: Nobody applied

- **WHEN** no fan has an Applied journey on any event of the series
- **THEN** the result is empty

### Requirement: A series is required for the applied fans

ListUserIDsAppliedSeries SHALL fail with InvalidArgument when no series is given.

#### Scenario: No series given

- **WHEN** ListUserIDsAppliedSeries is called without a series
- **THEN** it fails with InvalidArgument
