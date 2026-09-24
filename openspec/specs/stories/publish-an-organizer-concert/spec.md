# Publish an organizer concert

## Purpose

An organizer authors a concert for an Artist it represents, edits it while it is a draft, and publishes it; the published concert takes over matching discovered data and appears to fans according to its visibility.

## Requirements

### Requirement: Draft to published

A concert created with ConcertAuthoringUseCase.CreateDraft and edited with ConcertAuthoringUseCase.UpdateDraft SHALL stay out of every fan list until ConcertAuthoringUseCase.Publish succeeds; after that a PUBLIC concert SHALL appear in ConcertUseCase.ListByArtist for its performers, and an UNLISTED one SHALL NOT.

#### Scenario: Public concert goes live
- **WHEN** an organizer creates, edits and publishes a PUBLIC concert
- **THEN** ListByArtist for its performer returns the concert

#### Scenario: Unlisted concert stays off lists
- **WHEN** an organizer publishes an UNLISTED concert
- **THEN** ListByArtist for its performer does not return it

### Requirement: Published concert takes over discovered data

When a published PUBLIC concert's performance matches a discovered Concert's slot, that Concert SHALL become part of the organizer's Series with its id kept, and SHALL NOT be announced to followers again.

#### Scenario: Discovered concert claimed
- **WHEN** a discovered Concert exists at the slot of the organizer's performance and the organizer publishes
- **THEN** the Concert's Series is the organizer's Series and its id is unchanged

### Requirement: Cancelled concert leaves fan lists

After ConcertAuthoringUseCase.Cancel, the concert SHALL no longer appear in ConcertUseCase.ListByArtist.

#### Scenario: Cancel after publish
- **WHEN** the organizer cancels a published PUBLIC concert
- **THEN** ListByArtist for its performer no longer returns it
