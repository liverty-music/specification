# Spec Delta

## Purpose

Looks up a venue name typed by an operator in an external map catalog and returns the candidate places to choose from, each with its place id, canonical name and address.

## ADDED Requirements

### Requirement: Up to 5 candidates, best first

SearchPlaces SHALL take a text of 2 to 100 characters and return at most 5 places, best match first, each with its place id, its canonical name in Japanese when the catalog has one, and its address. Places in Japan SHALL rank before places elsewhere for the same match. It SHALL return an empty list when the catalog has no match, and SHALL fail with Unavailable when the catalog cannot be reached.

#### Scenario: Known venue

- **WHEN** "Zepp Haneda" is searched
- **THEN** at most 5 places are returned and the first is Zepp Haneda with its place id and its address in Japanese

#### Scenario: No match

- **WHEN** the catalog has no place matching the text
- **THEN** an empty list is returned

#### Scenario: Catalog down

- **WHEN** the catalog cannot be reached
- **THEN** SearchPlaces fails with Unavailable
