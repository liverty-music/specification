# Approve

## Purpose

Approve lets an admin publish a StagedConcert under the Series it was staged with, or, when it collides with an Event already in the catalog, resolve the collision by keeping the existing Event or adopting the staged details onto it.

## Requirements

### Requirement: Approve of a missing staged concert succeeds

When the StagedConcert does not exist (StagedConcert.GetByID NotFound) — already approved or rejected — Approve SHALL succeed with no conflict and change nothing.

#### Scenario: Double approval
- **WHEN** an admin approves a StagedConcert that a previous approval already removed
- **THEN** Approve succeeds and no Event is added

### Requirement: The venue is found or created

Approve SHALL find or create the Venue for the StagedConcert in this order: by resolved place id (Venue.GetByPlaceID); by listed venue name and admin area (Venue.GetByListedName), giving that Venue the resolved place id when it has none (Venue.BackfillPlaceID); otherwise by creating it (Venue.Create) with the resolved name — or the listed venue name when unresolved — the resolved place id and coordinates when present, and the listed venue name. The admin area used to look up and to create SHALL be the same: the resolved admin area when present, otherwise the discovered one.

#### Scenario: Unresolved staged concert
- **WHEN** a StagedConcert with no resolved place is approved and no Venue lists its name and admin area
- **THEN** a Venue named after the listed venue name, with no place id and no coordinates, is created

#### Scenario: Different place id for a stored venue
- **WHEN** the resolved place id matches no Venue but a Venue holds the listed venue name and admin area with no place id
- **THEN** that Venue is used and takes the resolved place id

### Requirement: Collision is detected before any change

After resolving the Venue, Approve SHALL look up the Events at that Venue and date (Concert.FindEventsByVenueAndDate). The StagedConcert collides with an Event there that has the same start time (or both have none), or, when the StagedConcert has no start time, with any Event there that has one. Detection SHALL be repeated on every call.

#### Scenario: Same slot
- **WHEN** an Event exists at the Venue, date and start time of the StagedConcert
- **THEN** the StagedConcert collides with it

#### Scenario: Unknown start next to a known start
- **WHEN** the StagedConcert has no start time and an Event there starts at 18:00
- **THEN** the StagedConcert collides with it

### Requirement: Conflict without a choice changes nothing

When the StagedConcert collides and no resolution is chosen, Approve SHALL change nothing and return a conflict carrying the existing Event's id, its Series title, listed venue name, date, start and open time, together with the StagedConcert and its Artist.

#### Scenario: First approval of a duplicate
- **WHEN** an admin approves a colliding StagedConcert without a resolution
- **THEN** a conflict is returned and neither the Event nor the StagedConcert changes

### Requirement: Keep existing

When the StagedConcert collides and the resolution is keep existing, Approve SHALL record it in the RejectedConcertLog (RejectedConcertLog.Append) with the reason "duplicate of existing event" followed by the Event id and the reviewing admin's identity when known, remove the StagedConcert (StagedConcert.Delete), leave the Event unchanged, and return no conflict.

#### Scenario: Admin keeps the existing event
- **WHEN** an admin approves a colliding StagedConcert choosing keep existing
- **THEN** the StagedConcert is logged as rejected and removed, and the Event is unchanged

### Requirement: Adopt staged

When the StagedConcert collides and the resolution is adopt staged, Approve SHALL replace the Event's listed venue name with the StagedConcert's (Concert.UpdateEventListedVenueName), fill the Event's unknown start and open time from it (Concert.FillEventStartTimes), leave its Venue, place id and Series title unchanged, remove the StagedConcert, and return no conflict.

#### Scenario: Admin adopts the staged details
- **WHEN** an admin approves a colliding StagedConcert choosing adopt staged
- **THEN** the Event lists the StagedConcert's venue name, gains any unknown time, and the StagedConcert is removed

#### Scenario: Known start time kept
- **WHEN** the Event starts at 18:00 and the StagedConcert has no start time and adopt staged is chosen
- **THEN** the Event still starts at 18:00 and lists the StagedConcert's venue name

### Requirement: Publish a non-colliding staged concert

When the StagedConcert does not collide, Approve SHALL ignore any resolution and:
- when it brings a start time and an Event at the Venue and date has none, fill that Event's times (Concert.FillEventStartTimes) and add nothing;
- otherwise add it as a Concert under the StagedConcert's Series with its Artist as performer (Concert.Create), never creating a Series.

It SHALL then announce the new concerts to followers for the Artist when Concert.Create reported any Event id — a failed announcement does not fail Approve — remove the StagedConcert, and, when nothing was added, remove the StagedConcert's Series if it is left with no Event and no StagedConcert (Series.DeleteOrphaned; a failure here does not fail Approve).

#### Scenario: New concert
- **WHEN** a non-colliding StagedConcert is approved
- **THEN** an Event is added under its Series, followers are told, and the StagedConcert is removed

#### Scenario: Tour stop joins its tour
- **WHEN** a StagedConcert staged from a TOUR series is approved
- **THEN** its Event belongs to that TOUR Series and no Series is created

#### Scenario: Fill only
- **WHEN** the StagedConcert starts at 18:00 and the only Event at its Venue and date has no start time
- **THEN** that Event now starts at 18:00, nothing is announced, and the StagedConcert is removed

#### Scenario: Last staged row of an empty series
- **WHEN** a fill-only approval removes the last StagedConcert of a Series with no Event
- **THEN** that Series is removed

### Requirement: Suppression is not checked on approval

Approve SHALL NOT consult SuppressedConcerts; an admin approval can publish a slot that was suppressed after the concert was staged.

#### Scenario: Slot suppressed after staging
- **WHEN** a StagedConcert's slot became suppressed after it was staged and it is approved without collision
- **THEN** it is published
