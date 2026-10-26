## MODIFIED Requirements

### Requirement: Blocked slots fail the whole publish

PublishEvents SHALL fail with FailedPrecondition, changing nothing, when any given Event's slot is held by an Event of another Organizer's Series or by a CANCELLED Event. A SuppressedConcert at the slot SHALL NOT block the publish.

#### Scenario: Suppressed slot
- **WHEN** one given DRAFT Event's slot matches a SuppressedConcert and no Event is at that slot
- **THEN** that Event becomes PUBLISHED and its id is returned

#### Scenario: Another Organizer's slot
- **WHEN** one given DRAFT Event's slot holds an Event of another Organizer's Series
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT

#### Scenario: Cancelled slot
- **WHEN** one given DRAFT Event's slot holds a CANCELLED Event
- **THEN** PublishEvents fails with FailedPrecondition and every given Event stays DRAFT
