## MODIFIED Requirements

### Requirement: Collision is detected before any change

After resolving the Venue, Approve SHALL look up the Events at that Venue and date (Concert.FindEventsByVenueAndDate) and the Events of the ConcertCandidate's Artist on its date (Concert.FindEventsByArtistAndDate). The ConcertCandidate collides with an Event at the Venue and date that has the same start time (or both have none); when the ConcertCandidate has no start time, with any Event there that has one; and, when it has a start time, with an Event of its Artist on its date with the same start time at another Venue. Detection SHALL be repeated on every call.

#### Scenario: Same slot
- **WHEN** an Event exists at the Venue, date and start time of the ConcertCandidate
- **THEN** the ConcertCandidate collides with it

#### Scenario: Unknown start next to a known start
- **WHEN** the ConcertCandidate has no start time and an Event there starts at 18:00
- **THEN** the ConcertCandidate collides with it

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

When the ConcertCandidate collides and the resolution is adopt the candidate, Approve SHALL add the Event's current listed venue name to its other listed venue names (Concert.AddOtherListedVenueName), replace the Event's listed venue name with the ConcertCandidate's (Concert.UpdateEventListedVenueName), fill the Event's unknown start and open time from it (Concert.FillEventStartTimes), make its Artist a performer of the Event (see "Another Artist's Event becomes a shared bill"), leave its Venue, place id and Series title unchanged, remove the ConcertCandidate, and return no conflict.

#### Scenario: Admin adopts the candidate's details
- **WHEN** an admin approves a colliding ConcertCandidate choosing adopt the candidate
- **THEN** the Event lists the ConcertCandidate's venue name, is still listed under its former name, gains any unknown time, and the ConcertCandidate is removed

#### Scenario: Known start time kept
- **WHEN** the Event starts at 18:00 and the ConcertCandidate has no start time and adopt the candidate is chosen
- **THEN** the Event still starts at 18:00 and lists the ConcertCandidate's venue name

## ADDED Requirements

### Requirement: Another Artist's Event becomes a shared bill

When a ConcertCandidate is resolved by keep existing or adopt the candidate against an Event its Artist does not perform at, Approve SHALL make the Artist a performer of that Event: when the Artist has an Event without a start time at the same Venue and date, by merging it into that Event (Concert.Merge), which tells nobody again; otherwise by storing the Artist's concert in that Event's slot (Concert.Create), which adds the Artist to the Event's performers and tells the Artist's followers (Concert.Created). An Event the Artist already performs at SHALL be left with its performers.

#### Scenario: Shared bill approved
- **WHEN** an admin approves a ConcertCandidate of SiM that collides with マキシマム ザ ホルモン's Event, choosing keep existing
- **THEN** that Event lists both Artists as performers, SiM's followers are told about it, and the ConcertCandidate is removed

#### Scenario: Artist's unknown-start event merged
- **WHEN** the ConcertCandidate's Artist has an Event without a start time at the Venue and date of the other Artist's colliding Event at 18:00, and the admin chooses adopt the candidate
- **THEN** the 18:00 Event lists both Artists, the Event without a start time is gone, and nobody is told again
