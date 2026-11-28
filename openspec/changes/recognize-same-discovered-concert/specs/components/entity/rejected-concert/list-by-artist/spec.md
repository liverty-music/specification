# Spec Delta

## Purpose

Lists the RejectedConcert entries of one Artist, so that discovery can leave out a listing an admin already settled.

## ADDED Requirements

### Requirement: Entries of an artist

ListByArtist SHALL return every RejectedConcert entry of the Artist with its local date, listed venue name and start time, and an empty list when there is none. It SHALL fail with InvalidArgument when the Artist is not given, and with Unavailable when the store cannot be reached.

#### Scenario: Two entries
- **WHEN** the Artist has two RejectedConcert entries and another Artist has one
- **THEN** the Artist's two entries are returned

#### Scenario: None
- **WHEN** the Artist has no RejectedConcert entry
- **THEN** an empty list is returned
