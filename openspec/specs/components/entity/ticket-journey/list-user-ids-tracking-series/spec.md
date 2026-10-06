# TicketJourney.ListUserIDsTrackingSeries

## Purpose

Returns the fans who are tracking any event of a series, which is the audience that hears about that series' ticket sales phases.

## Requirements

### Requirement: ListUserIDsTrackingSeries returns each tracking fan once

ListUserIDsTrackingSeries SHALL return every fan who has a journey with status Tracking on at least one event of the given series. Each fan SHALL appear once, however many events of the series they track. With each fan it SHALL return the fan's linked event, chosen as follows:

- the earliest upcoming event among those the fan tracks in the series
- otherwise, the earliest event among those the fan tracks in the series

An event is upcoming when its date is today or later. A fan whose journeys on the series are all in another status (Applied, Lost, Unpaid, Paid) SHALL NOT be returned. The result has no particular order. It SHALL be empty when nobody tracks any event of the series.

#### Scenario: Fans tracking events of the series

- **WHEN** fan A tracks two events of the series and fan B tracks one
- **THEN** the result contains fan A once and fan B once

#### Scenario: Linked event is the earliest upcoming tracked event

- **WHEN** fan A tracks the series' 1 November and 15 November events, and the series' earlier 20 October event is not tracked by fan A
- **THEN** fan A's linked event is the 1 November event

#### Scenario: Every tracked event is past

- **WHEN** fan A tracks only the series' 1 September and 5 September events and both are past
- **THEN** fan A's linked event is the 1 September event

#### Scenario: A fan past the Tracking stage

- **WHEN** fan C's only journey on the series is Applied
- **THEN** fan C is not in the result

#### Scenario: Tracking an event of another series

- **WHEN** fan D tracks only events of a different series
- **THEN** fan D is not in the result

#### Scenario: Nobody is tracking

- **WHEN** no fan has a Tracking journey on any event of the series
- **THEN** the result is empty

### Requirement: A series is required

ListUserIDsTrackingSeries SHALL fail with InvalidArgument when no series is given.

#### Scenario: No series given

- **WHEN** ListUserIDsTrackingSeries is called without a series
- **THEN** it fails with InvalidArgument
