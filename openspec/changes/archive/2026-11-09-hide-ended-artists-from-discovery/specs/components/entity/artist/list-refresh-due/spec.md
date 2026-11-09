# Spec Delta

## Purpose

Returns the artists whose details a daily run reads again from the music catalog: one fixed share of all registered artists, chosen by id, so that every artist is read again once per cycle.

## ADDED Requirements

### Requirement: ListRefreshDue returns one slot of all artists
ListRefreshDue SHALL take a slot count and a slot number from 0 to the slot count minus 1. Every artist SHALL belong to exactly one slot, derived from its id alone, so an artist stays in the same slot on every call with the same slot count, and the artists SHALL be spread over the slots in about equal numbers. ListRefreshDue SHALL return, with their id, name and MBID, every artist in the given slot, whether or not anyone follows it.

#### Scenario: Same slot on every call
- **WHEN** ListRefreshDue is called twice with slot count 30 and slot 7
- **THEN** both calls return the same artists, apart from artists registered between the calls

#### Scenario: Every artist in one slot
- **WHEN** ListRefreshDue is called with slot count 30 for each slot from 0 to 29
- **THEN** every registered artist is returned by exactly one of the 30 calls

#### Scenario: Spread over the slots
- **WHEN** 3,000 artists are registered and ListRefreshDue is called with slot count 30 for each slot
- **THEN** each call returns between 50 and 150 artists

#### Scenario: Empty slot
- **WHEN** no registered artist belongs to the given slot
- **THEN** an empty list is returned without error
