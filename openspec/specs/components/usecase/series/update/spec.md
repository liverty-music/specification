# Update

## Purpose

Update lets a member of the owning Organizer edit a concert: everything while it is a draft, and corrections — title, description, performers, doors-open and start times, and new draft dates — once it has published dates.

## Requirements

### Requirement: Only the owner

Update SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another Organizer's series
- **WHEN** a member updates a Series owned by another Organizer
- **THEN** Update fails with PermissionDenied

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** Update fails with PermissionDenied

### Requirement: Same validation as a new draft

Update SHALL reject unrepresented performers with PermissionDenied and invalid input with InvalidArgument exactly as Create does, except that the date of a PUBLISHED or CANCELLED Event is not checked against the current day. Each new or DRAFT event SHALL give the place id of a picked place, failing with InvalidArgument and changing nothing without one, and its Venue SHALL be found or created from that place as Create does. A PUBLISHED or CANCELLED Event SHALL NOT need a place id: its venue counts as unchanged when the given venue name equals its listed venue name and, when a place id is given and its Venue has one, the two place ids are equal, so a date published before venues were picked from the map catalog can still be corrected.

#### Scenario: Doors after start
- **WHEN** an updated event opens after it starts
- **THEN** Update fails with InvalidArgument

#### Scenario: Correcting a past published date
- **WHEN** a PUBLISHED Event dated yesterday is given unchanged with a new open time
- **THEN** Update does not fail for the date

#### Scenario: Published date without a place id
- **WHEN** the owner corrects the title of a Series whose PUBLISHED Event's Venue has no place id, giving that Event without a place id
- **THEN** the title is changed and the Event keeps its Venue

#### Scenario: New date without a place id
- **WHEN** the owner adds an event without an id and without a place id
- **THEN** Update fails with InvalidArgument and nothing changes

### Requirement: Corrections keep what publish fixed

Update SHALL read the Series with its Events (Series.GetAuthored) and fail with FailedPrecondition, changing nothing, when:
- a PUBLISHED or CANCELLED Event of the Series is not given, because a published date is cancelled, not removed;
- a given PUBLISHED Event's venue, date or per-account limit differs from the Event's;
- a given CANCELLED Event differs from the Event in any value;
- the Series has a PUBLISHED or CANCELLED Event and the given type, source page or visibility differ from the Series';
- a given PUBLISHED Event's start time differs from the Event's and TicketSale.ListByEvent returns at least one sale for the Event.

#### Scenario: Published venue changed
- **WHEN** the owner gives a PUBLISHED Event with another venue
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Published per-account limit changed
- **WHEN** the owner gives a PUBLISHED Event whose per-account limit is 4 with a limit of 2
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Published date left out
- **WHEN** the owner updates a Series and leaves out one of its PUBLISHED Events
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Visibility changed after publish
- **WHEN** the owner changes a Series with a PUBLISHED Event from PUBLIC to UNLISTED
- **THEN** Update fails with FailedPrecondition

#### Scenario: Start time on sale
- **WHEN** the owner changes the start time of a PUBLISHED Event that a TicketSale names
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Start time before any sale
- **WHEN** the owner sets the start time of a PUBLISHED Event that no TicketSale names
- **THEN** the start time is set

### Requirement: Edit applied

Update SHALL apply the edit (Series.Update), keeping the Series' id, Organizer and cover image, and return the Series with its Events and performers (Series.GetAuthored). A failure of Series.Update, such as a new start time whose slot is blocked, SHALL be returned unchanged. Nothing SHALL be announced, whether the Series is a draft or has PUBLISHED Events.

#### Scenario: Event removed
- **WHEN** a draft with two DRAFT Events is updated with one
- **THEN** the returned Series has one DRAFT Event

#### Scenario: Published concert corrected
- **WHEN** the owner changes the title and a PUBLISHED Event's doors-open time
- **THEN** the returned Series has the new title and doors-open time, the Event stays PUBLISHED and no follower is notified

#### Scenario: Additional date added as a draft
- **WHEN** the owner adds an event without an id to a Series with PUBLISHED Events
- **THEN** the returned Series has the new Event as DRAFT and no follower is notified
