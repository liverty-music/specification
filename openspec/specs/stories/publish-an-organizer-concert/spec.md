# Publish an Organizer concert

## Purpose

An Organizer authors a concert for an Artist it represents, edits it while it is a draft, and publishes it; the published concert takes over matching discovered data and appears to fans according to its visibility. After publish the organizer corrects it, adds dates that are published on their own, and cancels dates.

```mermaid
usecase-beta
direction LR
actor Member("member")
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Publish an organizer concert")
  SeriesUseCaseCreate("SeriesUseCase.Create")
  SeriesUseCaseUpdate("SeriesUseCase.Update")
  SeriesUseCasePublish("SeriesUseCase.Publish")
  SeriesUseCaseCancel("SeriesUseCase.Cancel")
  ConcertUseCaseListByArtist("ConcertUseCase.ListByArtist")
end
Member --> Goal
Goal ..> : include SeriesUseCaseCreate
Goal ..> : include SeriesUseCaseUpdate
Goal ..> : include SeriesUseCasePublish
Goal ..> : include SeriesUseCaseCancel
Goal ..> : include ConcertUseCaseListByArtist
Fan --> ConcertUseCaseListByArtist
```

## Requirements

### Requirement: Draft to published

A concert created with SeriesUseCase.Create and edited with SeriesUseCase.Update SHALL stay out of every fan list until SeriesUseCase.Publish succeeds; after that a PUBLIC concert SHALL appear in ConcertUseCase.ListByArtist for its performers, and an UNLISTED one SHALL NOT.

#### Scenario: Public concert goes live
- **WHEN** an Organizer creates, edits and publishes a PUBLIC concert
- **THEN** ListByArtist for its performer returns the concert

#### Scenario: Unlisted concert stays off lists
- **WHEN** an Organizer publishes an UNLISTED concert
- **THEN** ListByArtist for its performer does not return it

### Requirement: Published concert takes over discovered data

When a published PUBLIC concert's performance matches a discovered Concert's slot, that Concert SHALL become part of the Organizer's Series with its id kept, and SHALL NOT be announced to followers again.

#### Scenario: Discovered concert claimed
- **WHEN** a discovered Concert exists at the slot of the Organizer's performance and the Organizer publishes
- **THEN** the Concert's Series is the Organizer's Series and its id is unchanged

### Requirement: Cancelled concert leaves fan lists

After SeriesUseCase.Cancel, the concert SHALL no longer appear in ConcertUseCase.ListByArtist.

#### Scenario: Cancel after publish
- **WHEN** the Organizer cancels a published PUBLIC concert
- **THEN** ListByArtist for its performer no longer returns it

### Requirement: A published concert gains a date

A date added with SeriesUseCase.Update to a published PUBLIC concert SHALL stay out of every fan list until SeriesUseCase.Publish publishes it; then it SHALL appear in ConcertUseCase.ListByArtist next to the earlier dates, and followers of the performers SHALL be told about the new date only.

#### Scenario: Tour adds a date
- **WHEN** an Organizer adds a date to a published PUBLIC tour, checks ListByArtist, then publishes the date
- **THEN** ListByArtist does not return the new date before the publish and returns it with the earlier dates after, and the announcement carries only the new date

### Requirement: A published concert is corrected

SeriesUseCase.Update on a published concert SHALL change the title and doors-open time that ConcertUseCase.ListByArtist returns, and SHALL refuse to change a published date's venue.

#### Scenario: Doors-open time announced after publish
- **WHEN** an Organizer publishes a concert without a doors-open time and later sets it with Update
- **THEN** ListByArtist returns the concert with the doors-open time

#### Scenario: Venue cannot move after publish
- **WHEN** an Organizer updates a published date with another venue
- **THEN** Update fails with FailedPrecondition and ListByArtist still returns the original venue
