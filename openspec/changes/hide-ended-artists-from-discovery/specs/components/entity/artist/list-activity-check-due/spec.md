# Spec Delta

## Purpose

Returns the artists whose activity status a daily check reads from the music catalog: one fixed share of all registered artists, chosen by id, plus the artists registered recently.

## ADDED Requirements

### Requirement: ListActivityCheckDue returns one slot of all artists and the recent ones
ListActivityCheckDue SHALL take a slot count, a slot number from 0 to the slot count minus 1, and a time. Every artist SHALL belong to exactly one slot, derived from its id alone, so an artist stays in the same slot on every call with the same slot count, and the artists SHALL be spread over the slots in about equal numbers. ListActivityCheckDue SHALL return, with their id, name and MBID, every artist in the given slot and every artist registered after the given time, each artist at most once, whether or not anyone follows it.

#### Scenario: Same slot on every call
- **WHEN** ListActivityCheckDue is called twice with slot count 30 and slot 7
- **THEN** both calls return the same registered artists, apart from artists registered between the calls

#### Scenario: Every artist in one slot
- **WHEN** ListActivityCheckDue is called with slot count 30 for each slot 0 to 29 and a time after every registration
- **THEN** every registered artist is returned by exactly one of the 30 calls

#### Scenario: Recently registered artist in another slot
- **WHEN** an artist registered after the given time belongs to another slot
- **THEN** the artist is returned

#### Scenario: Recently registered artist in the given slot
- **WHEN** an artist registered after the given time belongs to the given slot
- **THEN** the artist is returned once

#### Scenario: No artists
- **WHEN** no artist is registered
- **THEN** an empty list is returned without error
