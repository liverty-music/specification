# components/entity/series/cancel-events Specification

## Purpose
Cancels chosen Events of a first-party Series: a PUBLISHED Event becomes CANCELLED, a DRAFT Event is removed, and a Series left with no Event is removed.

## Requirements

### Requirement: Cancel published events, remove drafts

CancelEvents SHALL take a Series and one or more of its Events and, together or not at all, make each given PUBLISHED Event CANCELLED, keeping it, and remove each given DRAFT Event. When the Series is then left with no Event, it SHALL remove the Series. It SHALL return the ids of the Events it made CANCELLED.

#### Scenario: One date of a tour cancelled
- **WHEN** one of three PUBLISHED Events of a Series is given
- **THEN** that Event is CANCELLED and kept, its id is returned, and the other two stay PUBLISHED

#### Scenario: Whole draft discarded
- **WHEN** every Event of a Series is DRAFT and all are given
- **THEN** the Events and the Series are removed and no id is returned

#### Scenario: Published and draft dates together
- **WHEN** a PUBLISHED Event and a DRAFT Event of a Series are given
- **THEN** the PUBLISHED Event is CANCELLED, the DRAFT Event is removed, and only the cancelled id is returned

### Requirement: Only cancellable events of the series

CancelEvents SHALL fail with FailedPrecondition, changing nothing, when a given Event is not an Event of the Series or is already CANCELLED, with NotFound when the Series does not exist, and with InvalidArgument when no Event is given.

#### Scenario: Already cancelled
- **WHEN** a given Event is CANCELLED
- **THEN** CancelEvents fails with FailedPrecondition and nothing changes

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** CancelEvents fails with NotFound

### Requirement: Each cancelled event is announced with it

When CancelEvents makes an Event CANCELLED, it SHALL announce that Event as cancelled (Event.Cancelled) together with the change: the cancellation and its announcement are stored or neither is. It SHALL announce nothing for a DRAFT Event it removes. When an announcement cannot be recorded, CancelEvents SHALL fail with Unavailable and change nothing.

#### Scenario: Two dates cancelled
- **WHEN** CancelEvents makes two PUBLISHED Events of a Series CANCELLED
- **THEN** each of the two Events is announced as cancelled once

#### Scenario: Draft removed
- **WHEN** CancelEvents removes a DRAFT Event
- **THEN** nothing is announced for it

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a cancelled Event cannot be recorded
- **THEN** CancelEvents fails with Unavailable and every given Event keeps its state
