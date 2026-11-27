## MODIFIED Requirements

### Requirement: Collision is detected before any change

After resolving the Venue, Approve SHALL look up the Events at that Venue and date (Concert.FindEventsByVenueAndDate) and the Events of the ConcertCandidate's Artist on its date (Concert.FindEventsByArtistAndDate). The ConcertCandidate collides with an Event at the Venue and date that has the same start time (or both have none); when the ConcertCandidate has no start time, with any Event there that has one; when it has a start time, with an Event of its Artist on its date with the same start time at another Venue, and with an Organizer's Event (one with a publish state) of its Artist at the Venue and date that has no start time. Detection SHALL be repeated on every call.

#### Scenario: Same slot
- **WHEN** an Event exists at the Venue, date and start time of the ConcertCandidate
- **THEN** the ConcertCandidate collides with it

#### Scenario: Unknown start next to a known start
- **WHEN** the ConcertCandidate has no start time and an Event there starts at 18:00
- **THEN** the ConcertCandidate collides with it

#### Scenario: Organizer's event without a start time
- **WHEN** the ConcertCandidate starts at 18:00 and its Artist's Organizer's PUBLISHED Event at the Venue and date has no start time
- **THEN** the ConcertCandidate collides with that Event, which is not filled

#### Scenario: Same artist at another venue
- **WHEN** the ConcertCandidate starts at 18:00 on 2027-08-28 and its Artist's Event on that date starts at 18:00 at another Venue
- **THEN** the ConcertCandidate collides with that Event

### Requirement: Keep existing

When the ConcertCandidate collides and the resolution is keep existing, Approve SHALL record it in the RejectedConcert (RejectedConcert.Append) with the reason "duplicate of existing event" followed by the Event id and the reviewing admin's identity when known, add the ConcertCandidate's listed venue name to the Event's other listed venue names (Concert.AddOtherListedVenueName), make its Artist a performer of the Event (see "Another Artist's Event becomes a shared bill"), remove the ConcertCandidate (ConcertCandidate.Delete), leave the Event's listed venue name, Venue and times unchanged, and return no conflict.

#### Scenario: Admin keeps the existing event
- **WHEN** an admin approves a colliding ConcertCandidate of the Event's own Artist choosing keep existing
- **THEN** the ConcertCandidate is logged as rejected and removed, the Event keeps its name and times, and it is also listed under the ConcertCandidate's name

#### Scenario: Same candidate found again
- **WHEN** after that, discovery finds the Artist's concert again under the ConcertCandidate's name at the same date and start time
- **THEN** nothing is stored and no ConcertCandidate is staged

### Requirement: Adopt the candidate

When the ConcertCandidate collides and the resolution is adopt the candidate, Approve SHALL replace the Event's listed venue name with the ConcertCandidate's, keeping the replaced name among its other listed venue names (Concert.UpdateEventListedVenueName), fill the Event's unknown start and open time from it (Concert.FillEventStartTimes), make its Artist a performer of the Event (see "Another Artist's Event becomes a shared bill"), leave its Venue, place id and Series title unchanged, remove the ConcertCandidate, and return no conflict. Against an Event with a publish state (an Organizer's Event), adopt the candidate SHALL fail with FailedPrecondition and change nothing.

#### Scenario: Admin adopts the candidate's details
- **WHEN** an admin approves a colliding ConcertCandidate choosing adopt the candidate
- **THEN** the Event lists the ConcertCandidate's venue name, is still listed under its former name, gains any unknown time, and the ConcertCandidate is removed

#### Scenario: Organizer's event not adopted onto
- **WHEN** an admin chooses adopt the candidate for a ConcertCandidate colliding with an Organizer's PUBLISHED Event
- **THEN** Approve fails with FailedPrecondition, the Event keeps its listed venue name and times, and the ConcertCandidate is kept

#### Scenario: Known start time kept
- **WHEN** the Event starts at 18:00 and the ConcertCandidate has no start time and adopt the candidate is chosen
- **THEN** the Event still starts at 18:00 and lists the ConcertCandidate's venue name

### Requirement: Publish a non-colliding concert candidate

When the ConcertCandidate does not collide, Approve SHALL ignore any resolution and:
- when it brings a start time and an Event of its Artist at the Venue and date has none, fill that Event's times (Concert.FillEventStartTimes) and add nothing; an Organizer's Event is never filled this way (see "Collision is detected before any change");
- otherwise add it as a Concert under the ConcertCandidate's Series with its Artist as performer (Concert.Create), never creating a Series. Concert.Create announces the new concert to the Artist's followers; when it fails, Approve SHALL fail with its error and keep the ConcertCandidate.

An Event at the Venue and date that its Artist does not perform at SHALL never be filled by Approve. It SHALL then remove the ConcertCandidate. A Series left with no Event and no ConcertCandidate stays until the daily removal of empty discovered Series.

#### Scenario: New concert
- **WHEN** a non-colliding ConcertCandidate is approved
- **THEN** an Event is added under its Series and the ConcertCandidate is removed

#### Scenario: Tour stop joins its tour
- **WHEN** a ConcertCandidate staged from a TOUR series is approved
- **THEN** its Event belongs to that TOUR Series and no Series is created

#### Scenario: Fill only
- **WHEN** the ConcertCandidate starts at 18:00 and its Artist's only Event at its Venue and date has no start time
- **THEN** that Event now starts at 18:00, no Event is added, and the ConcertCandidate is removed

#### Scenario: Another artist's unknown-start event is not filled
- **WHEN** the ConcertCandidate starts at 18:00 and the only Event at its Venue and date is another Artist's, without a start time
- **THEN** a new Event at 18:00 with the ConcertCandidate's Artist is added and the other Event still has no start time

#### Scenario: Concert cannot be added
- **WHEN** Concert.Create fails with Unavailable
- **THEN** Approve fails with Unavailable and the ConcertCandidate is kept, so the admin can approve it again

#### Scenario: Last staged row of an empty series
- **WHEN** a fill-only approval removes the last ConcertCandidate of a Series with no Event
- **THEN** that Series is kept by Approve

## ADDED Requirements

### Requirement: Another Artist's Event becomes a shared bill

When a ConcertCandidate is resolved by keep existing or adopt the candidate against an Event its Artist does not perform at and that has no publish state, Approve SHALL make the Artist a performer of that Event: when the Artist has an Event without a start time and without a publish state at the same Venue and date, by merging it into that Event (Concert.Merge), which tells nobody again, leaving the merged Event's Series in place; otherwise, or when Merge refuses because the Artist's Event is the last of a Series with a TicketSale, by storing the Artist's concert in that Event's slot (Concert.Create), which adds the Artist to the Event's performers and tells the Artist's followers (Concert.Created). When Merge fails for another reason, such as Unavailable, Approve SHALL fail and keep the ConcertCandidate. An Event the Artist already performs at, and an Event with a publish state, SHALL be left with their performers.

#### Scenario: Shared bill approved
- **WHEN** an admin approves a ConcertCandidate of SiM that collides with マキシマム ザ ホルモン's Event, choosing keep existing
- **THEN** that Event lists both Artists as performers, SiM's followers are told about it, and the ConcertCandidate is removed

#### Scenario: Organizer's event kept as it is
- **WHEN** an admin approves a ConcertCandidate that collides with an Organizer's PUBLISHED Event, choosing keep existing
- **THEN** that Event's performers are unchanged and the ConcertCandidate is removed

#### Scenario: Merge cannot run
- **WHEN** Merge fails with Unavailable while a shared bill is resolved
- **THEN** Approve fails with Unavailable, Concert.Create is not called, and the ConcertCandidate is kept

#### Scenario: Artist's unknown-start event merged
- **WHEN** the ConcertCandidate's Artist has an Event without a start time at the Venue and date of the other Artist's colliding Event at 18:00, and the admin chooses adopt the candidate
- **THEN** the 18:00 Event lists both Artists, the Event without a start time is gone, and nobody is told again

#### Scenario: Tour with a ticket sale is kept
- **WHEN** the same holds but the Artist's Event without a start time is the only Event of a Series with a discovered TicketSale
- **THEN** that Event and its Series' TicketSale stay, and the 18:00 Event lists both Artists
