# Spec Delta

## Purpose

Publishes chosen DRAFT Events of a first-party Series into the catalog, claiming matching discovered Events, and returns the ids of the Events it newly added.

## ADDED Requirements

### Requirement: Draft events become published

PublishEvents SHALL take a Series and one or more of its DRAFT Events. For each given Event, at its Venue, date and start time (an unknown start matching only an unknown start), it SHALL:
- make the Event PUBLISHED when no Event that is not DRAFT is at that slot;
- remove the DRAFT Event when a PUBLISHED Event of this Series is already at that slot;
- claim the Event at that slot when it belongs to a discovered Series or to another Series of the same Organizer and is not CANCELLED: move it to this Series, keep its id, make it PUBLISHED, add the DRAFT Event's performers to it, and remove the DRAFT Event.

It SHALL return the ids of the Events it made PUBLISHED in place; claimed Events SHALL NOT be returned. Together with the Events, it SHALL remove the StagedConcerts that belong to the Series.

#### Scenario: New slot
- **WHEN** no Event is at a given DRAFT Event's slot
- **THEN** that Event becomes PUBLISHED and its id is returned

#### Scenario: Claim a discovered event
- **WHEN** a discovered Event with id E is at a given DRAFT Event's slot
- **THEN** E moves to the Series, keeps its id, becomes PUBLISHED, gains the draft's performers, is not returned, and the DRAFT Event is gone

#### Scenario: Known start next to unknown-start event
- **WHEN** a given DRAFT Event starts at 18:00 and the only Event at its Venue and date has no start time
- **THEN** the DRAFT Event becomes PUBLISHED and its id is returned

#### Scenario: Other drafts stay drafts
- **WHEN** a Series has two DRAFT Events and only one is given
- **THEN** only the given one is published and the other stays DRAFT

### Requirement: Blocked slots fail the whole publish

PublishEvents SHALL fail with FailedPrecondition, changing nothing, when any given Event's slot is suppressed, is held by an Event of another Organizer's Series, or is held by a CANCELLED Event.

#### Scenario: Suppressed slot
- **WHEN** one given DRAFT Event's slot matches a SuppressedConcert
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Another organizer's slot
- **WHEN** one given DRAFT Event's slot holds an Event of another Organizer's Series
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Cancelled slot
- **WHEN** one given DRAFT Event's slot holds a CANCELLED Event
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

### Requirement: Only drafts of the series

PublishEvents SHALL fail with FailedPrecondition, changing nothing, when a given Event is not a DRAFT Event of the Series, with NotFound when the Series does not exist, and with InvalidArgument when no Event is given.

#### Scenario: Already published
- **WHEN** a given Event is already PUBLISHED
- **THEN** PublishEvents fails with FailedPrecondition

#### Scenario: No event given
- **WHEN** PublishEvents is called with no Event
- **THEN** it fails with InvalidArgument
