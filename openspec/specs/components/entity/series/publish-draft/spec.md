# Series.PublishDraft

## Purpose

Turns a DRAFT first-party Series' DraftEvents into Events in the catalog, claiming matching discovered Events, marks the Series PUBLISHED, and returns the ids of the Events it newly added.

## Requirements

### Requirement: Draft events become events

For each DraftEvent, PublishDraft SHALL, at the DraftEvent's Venue, date and start time (an unknown start matching only an unknown start):
- add a new Event under the Series with the draft performers when no Event is there;
- leave the Event alone when it already belongs to this Series;
- claim the Event when it belongs to a discovered Series or another Series of the same Organizer: move it to this Series, keep its id, and add the draft performers to it.

It SHALL return the ids of the added Events only; claimed Events SHALL NOT be returned.

#### Scenario: New slot
- **WHEN** no Event is at a DraftEvent's slot
- **THEN** a new Event is added under the Series and its id returned

#### Scenario: Claim a discovered event
- **WHEN** a discovered Event with id E is at a DraftEvent's slot
- **THEN** E moves to the Series, keeps its id, gains the draft performers, and is not returned

#### Scenario: Known start next to unknown-start event
- **WHEN** a DraftEvent starts at 18:00 and the only Event at its Venue and date has no start time
- **THEN** a new Event starting at 18:00 is added

### Requirement: Blocked slots fail the whole publish

PublishDraft SHALL fail with FailedPrecondition, changing nothing, when any DraftEvent's slot is suppressed or is held by an Event of another Organizer's Series.

#### Scenario: Suppressed slot
- **WHEN** one DraftEvent's slot matches a SuppressedConcert
- **THEN** PublishDraft fails with FailedPrecondition and the Series stays DRAFT

#### Scenario: Another organizer's slot
- **WHEN** one DraftEvent's slot holds an Event of another Organizer's Series
- **THEN** PublishDraft fails with FailedPrecondition and the Series stays DRAFT

### Requirement: Publish completes the draft

On success PublishDraft SHALL, together with the Events: remove the Series' DraftEvents and draft performers, remove StagedConcerts that belong to the Series, and set the Series PUBLISHED with the given published-at time. It SHALL fail with FailedPrecondition when the Series is not DRAFT, and with NotFound when it does not exist.

#### Scenario: Draft cleared
- **WHEN** PublishDraft succeeds
- **THEN** the Series is PUBLISHED and has no DraftEvents

#### Scenario: Already published
- **WHEN** PublishDraft is called on a PUBLISHED Series
- **THEN** it fails with FailedPrecondition
