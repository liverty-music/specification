# Spec Delta

## MODIFIED Requirements

### Requirement: Draft to published

A concert created with ConcertAuthoringUseCase.CreateDraft and edited with ConcertAuthoringUseCase.Update SHALL stay out of every fan list until ConcertAuthoringUseCase.Publish succeeds; after that a PUBLIC concert SHALL appear in ConcertUseCase.ListByArtist for its performers, and an UNLISTED one SHALL NOT.

#### Scenario: Public concert goes live
- **WHEN** an organizer creates, edits and publishes a PUBLIC concert
- **THEN** ListByArtist for its performer returns the concert

#### Scenario: Unlisted concert stays off lists
- **WHEN** an organizer publishes an UNLISTED concert
- **THEN** ListByArtist for its performer does not return it

## ADDED Requirements

### Requirement: A published concert gains a date

A date added with ConcertAuthoringUseCase.Update to a published PUBLIC concert SHALL stay out of every fan list until ConcertAuthoringUseCase.Publish publishes it; then it SHALL appear in ConcertUseCase.ListByArtist next to the earlier dates, and followers of the performers SHALL be told about the new date only.

#### Scenario: Tour adds a date
- **WHEN** an organizer adds a date to a published PUBLIC tour, checks ListByArtist, then publishes the date
- **THEN** ListByArtist does not return the new date before the publish and returns it with the earlier dates after, and the announcement carries only the new date

### Requirement: A published concert is corrected

ConcertAuthoringUseCase.Update on a published concert SHALL change the title and doors-open time that ConcertUseCase.ListByArtist returns, and SHALL refuse to change a published date's venue.

#### Scenario: Doors-open time announced after publish
- **WHEN** an organizer publishes a concert without a doors-open time and later sets it with Update
- **THEN** ListByArtist returns the concert with the doors-open time

#### Scenario: Venue cannot move after publish
- **WHEN** an organizer updates a published date with another venue
- **THEN** Update fails with FailedPrecondition and ListByArtist still returns the original venue
