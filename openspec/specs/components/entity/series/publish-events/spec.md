# components/entity/series/publish-events Specification

## Purpose
Publishes chosen DRAFT Events of a first-party Series into the catalog, claiming matching discovered Events, and returns the ids of the Events it newly added.

## Requirements

### Requirement: Draft events become published

PublishEvents SHALL take a Series and one or more of its DRAFT Events. For each given Event, at its Venue, date and start time (an unknown start matching only an unknown start), it SHALL:
- make the Event PUBLISHED when no Event that is not DRAFT is at that slot;
- remove the DRAFT Event when a PUBLISHED Event of this Series is already at that slot;
- claim the Event at that slot when it belongs to a discovered Series: move it to this Series, keep its id, make it PUBLISHED, add the performers of the DRAFT Event's Concert to its Concert, and remove the DRAFT Event.

It SHALL return the ids of the Events it made PUBLISHED in place; claimed Events SHALL NOT be returned. Together with the Events, it SHALL remove the ConcertCandidates that belong to the Series.

#### Scenario: New slot
- **WHEN** no Event is at a given DRAFT Event's slot
- **THEN** that Event becomes PUBLISHED and its id is returned

#### Scenario: Claim a discovered event
- **WHEN** a discovered Event with id E is at a given DRAFT Event's slot
- **THEN** E moves to the Series, keeps its id, becomes PUBLISHED, its Concert gains the draft's performers, is not returned, and the DRAFT Event is gone

#### Scenario: Known start next to unknown-start event
- **WHEN** a given DRAFT Event starts at 18:00 and the only Event at its Venue and date has no start time
- **THEN** the DRAFT Event becomes PUBLISHED and its id is returned

#### Scenario: Other drafts stay drafts
- **WHEN** a Series has two DRAFT Events and only one is given
- **THEN** only the given one is published and the other stays DRAFT

### Requirement: Blocked slots fail the whole publish

PublishEvents SHALL fail with FailedPrecondition, changing nothing, when any given Event's slot is held by an Event of another first-party Series, whether that Series belongs to another Organizer or to the same one, or by a CANCELLED Event. A SuppressedConcert at the slot SHALL NOT block the publish.

#### Scenario: Suppressed slot
- **WHEN** one given DRAFT Event's slot matches a SuppressedConcert and no Event is at that slot
- **THEN** that Event becomes PUBLISHED and its id is returned

#### Scenario: Another Organizer's slot
- **WHEN** one given DRAFT Event's slot holds an Event of another Organizer's Series
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Slot of another Series of the same Organizer
- **WHEN** one given DRAFT Event's slot holds a PUBLISHED Event of another Series of the same Organizer, with its own visibility, SeatTypes and TicketSales
- **THEN** PublishEvents fails with FailedPrecondition, every given Event stays DRAFT, and the held Event stays in its Series with its visibility, SeatTypes and TicketSales unchanged

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

### Requirement: New concerts of a public series are announced with the publish

When PublishEvents makes at least one Event PUBLISHED in place and the Series' visibility is PUBLIC, it SHALL announce the new concerts as created (Concert.Created) once for each performing Artist of those Events: one announcement per Artist, carrying the Concerts made PUBLISHED in place by this call at which that Artist performs, together with the publish: both are stored or neither is. Claimed Events, Events published before, and every Event of an UNLISTED Series SHALL NOT be announced. When PublishEvents fails it SHALL announce nothing. When an announcement cannot be recorded, PublishEvents SHALL fail with Unavailable and every given Event SHALL stay DRAFT.

#### Scenario: Two performers

- **WHEN** PublishEvents makes one Event of a PUBLIC Series with two performers PUBLISHED
- **THEN** two announcements are made, one per performer, each carrying that Concert

#### Scenario: Additional date announced alone

- **WHEN** a PUBLIC Series has three PUBLISHED Events and PublishEvents makes a fourth PUBLISHED
- **THEN** each announcement carries only the fourth Concert

#### Scenario: Only claimed events

- **WHEN** every given DRAFT Event claims an Event of a discovered Series
- **THEN** nothing is announced

#### Scenario: Unlisted series

- **WHEN** PublishEvents makes an Event of an UNLISTED Series PUBLISHED
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** PublishEvents would make an Event of a PUBLIC Series PUBLISHED and the announcement cannot be recorded
- **THEN** PublishEvents fails with Unavailable and every given Event stays DRAFT

### Requirement: Share token stored with the publish

PublishEvents SHALL take an optional share token. When one is given, PublishEvents SHALL make it the Series' share token together with the publish: both are stored or neither is. A share token SHALL be given only for an UNLISTED Series that has no share token yet: PublishEvents SHALL fail with FailedPrecondition, changing nothing, when the Series is not UNLISTED or already has one, and with AlreadyExists, changing nothing, when another Series holds the given token. When PublishEvents fails for any reason, the Series SHALL keep the share token it had before.

#### Scenario: Token stored with the first publish

- **WHEN** PublishEvents is given a DRAFT Event of an UNLISTED Series without a share token, and the token T
- **THEN** the Event is PUBLISHED and T opens the Series

#### Scenario: Blocked publish stores no token

- **WHEN** PublishEvents is given the token T for an UNLISTED Series without a share token and a given Event's slot is held by a CANCELLED Event
- **THEN** PublishEvents fails with FailedPrecondition, every given Event stays DRAFT and the Series has no share token

#### Scenario: Token for a public series

- **WHEN** PublishEvents is given a share token for a PUBLIC Series
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Series already has a token

- **WHEN** PublishEvents is given a share token for an UNLISTED Series that already has the token T1
- **THEN** PublishEvents fails with FailedPrecondition, every given Event stays DRAFT and T1 still opens the Series

#### Scenario: Token held by another series

- **WHEN** PublishEvents is given a share token that another Series holds
- **THEN** PublishEvents fails with AlreadyExists, every given Event stays DRAFT and the Series has no share token
