# Approve

## Purpose

Approve lets an admin publish a ConcertCandidate under the Series it was proposed with, or, when it collides with an Event already in the catalog, resolve the collision by keeping the existing Event or adopting the candidate's details onto it.

## Requirements

### Requirement: Approve of a missing concert candidate succeeds

When the ConcertCandidate does not exist (ConcertCandidate.GetByID NotFound) — already approved or rejected — Approve SHALL succeed with no conflict and change nothing.

#### Scenario: Double approval
- **WHEN** an admin approves a ConcertCandidate that a previous approval already removed
- **THEN** Approve succeeds and no Event is added

### Requirement: The venue is found or created

Approve SHALL find or create the Venue for the ConcertCandidate in this order: by resolved place id (Venue.GetByPlaceID); by listed venue name and admin area (Venue.GetByListedName), giving that Venue the resolved place id when it has none (Venue.BackfillPlaceID); otherwise by creating it (Venue.Create) with the resolved name — or the listed venue name when unresolved — the resolved place id and coordinates when present, and the listed venue name. The admin area used to look up and to create SHALL be the same: the resolved admin area when present, otherwise the discovered one.

#### Scenario: Unresolved concert candidate
- **WHEN** a ConcertCandidate with no resolved place is approved and no Venue lists its name and admin area
- **THEN** a Venue named after the listed venue name, with no place id and no coordinates, is created

#### Scenario: Different place id for a stored venue
- **WHEN** the resolved place id matches no Venue but a Venue holds the listed venue name and admin area with no place id
- **THEN** that Venue is used and takes the resolved place id

### Requirement: Collision is detected before any change

After resolving the Venue, Approve SHALL look up the Events at that Venue and date (Concert.FindEventsByVenueAndDate). The ConcertCandidate collides with an Event there that has the same start time (or both have none), or, when the ConcertCandidate has no start time, with any Event there that has one. Detection SHALL be repeated on every call.

#### Scenario: Same slot
- **WHEN** an Event exists at the Venue, date and start time of the ConcertCandidate
- **THEN** the ConcertCandidate collides with it

#### Scenario: Unknown start next to a known start
- **WHEN** the ConcertCandidate has no start time and an Event there starts at 18:00
- **THEN** the ConcertCandidate collides with it

### Requirement: Conflict without a choice changes nothing

When the ConcertCandidate collides and no resolution is chosen, Approve SHALL change nothing and return a conflict carrying the existing Event's id, its Series title, listed venue name, date, start and open time, together with the ConcertCandidate and its Artist.

#### Scenario: First approval of a duplicate
- **WHEN** an admin approves a colliding ConcertCandidate without a resolution
- **THEN** a conflict is returned and neither the Event nor the ConcertCandidate changes

### Requirement: Keep existing

When the ConcertCandidate collides and the resolution is keep existing, Approve SHALL record it in the RejectedConcert (RejectedConcert.Append) with the reason "duplicate of existing event" followed by the Event id and the reviewing admin's identity when known, remove the ConcertCandidate (ConcertCandidate.Delete), leave the Event unchanged, and return no conflict.

#### Scenario: Admin keeps the existing event
- **WHEN** an admin approves a colliding ConcertCandidate choosing keep existing
- **THEN** the ConcertCandidate is logged as rejected and removed, and the Event is unchanged

### Requirement: Adopt the candidate

When the ConcertCandidate collides and the resolution is adopt the candidate, Approve SHALL replace the Event's listed venue name with the ConcertCandidate's (Concert.UpdateEventListedVenueName), fill the Event's unknown start and open time from it (Concert.FillEventStartTimes), leave its Venue, place id and Series title unchanged, remove the ConcertCandidate, and return no conflict.

#### Scenario: Admin adopts the candidate's details
- **WHEN** an admin approves a colliding ConcertCandidate choosing adopt the candidate
- **THEN** the Event lists the ConcertCandidate's venue name, gains any unknown time, and the ConcertCandidate is removed

#### Scenario: Known start time kept
- **WHEN** the Event starts at 18:00 and the ConcertCandidate has no start time and adopt the candidate is chosen
- **THEN** the Event still starts at 18:00 and lists the ConcertCandidate's venue name

### Requirement: Publish a non-colliding concert candidate

When the ConcertCandidate does not collide, Approve SHALL ignore any resolution and:
- when it brings a start time and an Event at the Venue and date has none, fill that Event's times (Concert.FillEventStartTimes) and add nothing;
- otherwise add it as a Concert under the ConcertCandidate's Series with its Artist as performer (Concert.Create), never creating a Series.

It SHALL then announce the new concerts to followers for the Artist when Concert.Create reported any Event id — a failed announcement does not fail Approve — remove the ConcertCandidate, and, when nothing was added, remove the ConcertCandidate's Series if it is left with no Event and no ConcertCandidate (Series.DeleteOrphaned; a failure here does not fail Approve).

#### Scenario: New concert
- **WHEN** a non-colliding ConcertCandidate is approved
- **THEN** an Event is added under its Series, followers are told, and the ConcertCandidate is removed

#### Scenario: Tour stop joins its tour
- **WHEN** a ConcertCandidate staged from a TOUR series is approved
- **THEN** its Event belongs to that TOUR Series and no Series is created

#### Scenario: Fill only
- **WHEN** the ConcertCandidate starts at 18:00 and the only Event at its Venue and date has no start time
- **THEN** that Event now starts at 18:00, nothing is announced, and the ConcertCandidate is removed

#### Scenario: Last staged row of an empty series
- **WHEN** a fill-only approval removes the last ConcertCandidate of a Series with no Event
- **THEN** that Series is removed

### Requirement: Suppression is not checked on approval

Approve SHALL NOT consult SuppressedConcerts; an admin approval can publish a slot that was suppressed after the concert was staged.

#### Scenario: Slot suppressed after staging
- **WHEN** a ConcertCandidate's slot became suppressed after it was staged and it is approved without collision
- **THEN** it is published
