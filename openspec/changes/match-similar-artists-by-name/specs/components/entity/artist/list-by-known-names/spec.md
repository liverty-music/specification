## Purpose

Finds the registered artists that have any of the given names, so a result the listening service lists only by name can be matched to a registered artist.

## ADDED Requirements

### Requirement: ListByKnownNames returns every artist that has one of the names
ListByKnownNames SHALL take names and return every registered artist that has at least one of them, each artist once, whatever its mbid_status and activity_ended. When no artist has any of them, or no name is given, it SHALL return an empty list without error.

#### Scenario: Found by an alias
- **WHEN** ListByKnownNames is called with `Yorushika` and the artist `ヨルシカ` has that alias
- **THEN** it returns that artist

#### Scenario: Two artists share a name
- **WHEN** two registered artists have the name `tomoo` and ListByKnownNames is called with it
- **THEN** it returns both

#### Scenario: Several names of one artist
- **WHEN** ListByKnownNames is called with two names of the same artist
- **THEN** it returns that artist once

#### Scenario: No artist
- **WHEN** no registered artist has any given name
- **THEN** it returns an empty list

#### Scenario: Empty input
- **WHEN** ListByKnownNames is called with no names
- **THEN** it returns an empty list
