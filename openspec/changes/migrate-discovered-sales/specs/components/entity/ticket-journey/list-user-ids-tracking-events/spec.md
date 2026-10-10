# Spec Delta

## Purpose

Returns the fans who are tracking any of the given events, each with one linked event among them, which is the audience that hears about an Organizer's ticket sale offering those events.

## ADDED Requirements

### Requirement: ListUserIDsTrackingEvents returns each tracking fan once

ListUserIDsTrackingEvents SHALL return every fan who has a journey with status Tracking on at least one of the given events. Each fan SHALL appear once, however many of the events they track. With each fan it SHALL return the fan's linked event, chosen among the given events the fan tracks as follows:

- the earliest upcoming event
- otherwise, the earliest event

An event is upcoming when its date is today or later. A fan whose journeys on the given events are all in another status (Applied, Lost, Unpaid, Paid) SHALL NOT be returned. The result has no particular order. It SHALL be empty when nobody tracks any of the events or when no event is given.

#### Scenario: Fans tracking offered events
- **WHEN** fan A tracks two of the given events and fan B tracks one
- **THEN** the result contains fan A once and fan B once

#### Scenario: Linked event is among the given events
- **WHEN** fan A tracks the series' 20 October event, which is not given, and its 1 November event, which is given
- **THEN** fan A's linked event is the 1 November event

#### Scenario: Tracking only an event not given
- **WHEN** fan C tracks only an event of the series that is not given
- **THEN** fan C is not in the result

#### Scenario: A fan past the Tracking stage
- **WHEN** fan D's only journey on the given events is Applied
- **THEN** fan D is not in the result

#### Scenario: No event given
- **WHEN** ListUserIDsTrackingEvents is called with no event
- **THEN** the result is empty
