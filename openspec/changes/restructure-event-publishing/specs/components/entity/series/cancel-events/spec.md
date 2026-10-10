# Spec Delta

## Purpose

Cancels chosen Events of a first-party Series: a PUBLISHED Event becomes CANCELLED, a DRAFT Event is removed, and a Series left with no Event is removed.

## ADDED Requirements

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
