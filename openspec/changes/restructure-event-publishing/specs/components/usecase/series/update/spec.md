# Spec Delta

## Purpose

Update lets the owning organizer operator edit a concert: everything while it is a draft, and corrections — title, description, doors-open and start times, and new draft dates — once it has published dates.

## ADDED Requirements

### Requirement: Only the owner

Update SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another organizer's series
- **WHEN** an operator updates a Series owned by another Organizer
- **THEN** Update fails with PermissionDenied

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** Update fails with PermissionDenied

### Requirement: Same validation as a new draft

Update SHALL reject unrepresented performers with PermissionDenied and invalid input with InvalidArgument exactly as CreateDraft does, except that the date of a PUBLISHED or CANCELLED Event is not checked against the current day. It SHALL find or create the Venue of each new or DRAFT event as CreateDraft does.

#### Scenario: Doors after start
- **WHEN** an updated event opens after it starts
- **THEN** Update fails with InvalidArgument

#### Scenario: Correcting a past published date
- **WHEN** a PUBLISHED Event dated yesterday is given unchanged with a new open time
- **THEN** Update does not fail for the date

### Requirement: Corrections keep what publish fixed

Update SHALL read the Series with its Events (Series.GetAuthored) and fail with FailedPrecondition, changing nothing, when:
- a PUBLISHED or CANCELLED Event of the Series is not given, because a published date is cancelled, not removed;
- a given PUBLISHED Event's venue or date differs from the Event's;
- a given CANCELLED Event differs from the Event in any value;
- the Series has a PUBLISHED or CANCELLED Event and the given type, source page or visibility differ from the Series';
- a given PUBLISHED Event's start time differs from the Event's and TicketSale.ListByEvent returns at least one sale for the Event.

#### Scenario: Published venue changed
- **WHEN** the owner gives a PUBLISHED Event with another venue
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Published date left out
- **WHEN** the owner updates a Series and leaves out one of its PUBLISHED Events
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Visibility changed after publish
- **WHEN** the owner changes a Series with a PUBLISHED Event from PUBLIC to UNLISTED
- **THEN** Update fails with FailedPrecondition

#### Scenario: Start time on sale
- **WHEN** the owner changes the start time of a PUBLISHED Event that a TicketSale offers
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Start time before any sale
- **WHEN** the owner sets the start time of a PUBLISHED Event that no TicketSale offers
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
