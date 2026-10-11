# ConcertCandidate.ListPendingDedupKeysByArtist

## Purpose

Lists the date and listed venue name of every ConcertCandidate pending for one Artist, for comparing new discoveries before their venues are resolved.

## Requirements

### Requirement: Keys of an artist's pending rows

ListPendingDedupKeysByArtist SHALL return the local date and listed venue name of each ConcertCandidate discovered for the Artist, and an empty list when there is none.

#### Scenario: Two pending rows
- **WHEN** the Artist has two ConcertCandidates
- **THEN** two date and listed venue name pairs are returned

#### Scenario: None pending
- **WHEN** the Artist has no ConcertCandidate
- **THEN** an empty list is returned
