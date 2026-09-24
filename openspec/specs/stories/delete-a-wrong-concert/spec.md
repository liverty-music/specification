# Delete a wrong concert

## Purpose

An admin removes a wrong Concert from the catalog for good: neither the next discovery run nor an organizer's publish brings the same slot back.

## Requirements

### Requirement: A deleted slot stays deleted

After AdminConcertUseCase.Delete removes a Concert, its Venue, date and start time SHALL stay suppressed: ConcertCreationUseCase.CreateFromDiscovered SHALL neither publish nor stage a concert at that slot, and ConcertAuthoringUseCase.Publish SHALL refuse a draft with a performance at that slot. No usecase removes the suppression.

#### Scenario: Discovery finds it again
- **WHEN** an admin deletes a Concert and a later search finds the same slot for another Artist
- **THEN** no Concert and no StagedConcert exists for that slot

#### Scenario: Organizer publishes into the slot
- **WHEN** an organizer publishes a draft with a performance at the deleted slot
- **THEN** the publish fails with FailedPrecondition
