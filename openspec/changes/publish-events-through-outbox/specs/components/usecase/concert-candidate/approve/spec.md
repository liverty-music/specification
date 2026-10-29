## MODIFIED Requirements

### Requirement: Publish a non-colliding concert candidate

When the ConcertCandidate does not collide, Approve SHALL ignore any resolution and:
- when it brings a start time and an Event at the Venue and date has none, fill that Event's times (Concert.FillEventStartTimes) and add nothing;
- otherwise add it as a Concert under the ConcertCandidate's Series with its Artist as performer (Concert.Create), never creating a Series. Concert.Create announces the new concert to the Artist's followers; when it fails, Approve SHALL fail with its error and keep the ConcertCandidate.

It SHALL then remove the ConcertCandidate, and, when nothing was added, remove the ConcertCandidate's Series if it is left with no Event and no ConcertCandidate (Series.DeleteOrphaned; a failure here does not fail Approve).

#### Scenario: New concert
- **WHEN** a non-colliding ConcertCandidate is approved
- **THEN** an Event is added under its Series and the ConcertCandidate is removed

#### Scenario: Tour stop joins its tour
- **WHEN** a ConcertCandidate staged from a TOUR series is approved
- **THEN** its Event belongs to that TOUR Series and no Series is created

#### Scenario: Fill only
- **WHEN** the ConcertCandidate starts at 18:00 and the only Event at its Venue and date has no start time
- **THEN** that Event now starts at 18:00, no Event is added, and the ConcertCandidate is removed

#### Scenario: Concert cannot be added
- **WHEN** Concert.Create fails with Unavailable
- **THEN** Approve fails with Unavailable and the ConcertCandidate is kept, so the admin can approve it again

#### Scenario: Last staged row of an empty series
- **WHEN** a fill-only approval removes the last ConcertCandidate of a Series with no Event
- **THEN** that Series is removed
