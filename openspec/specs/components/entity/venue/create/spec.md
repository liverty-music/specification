# Venue.Create

## Purpose

Stores a new Venue, or returns the Venue that already holds the same place id or the same listed venue name and admin area.

## Requirements

### Requirement: Create is get-or-create

Create SHALL store the Venue and return its id when no Venue holds its place id and no Venue holds its listed venue name with the same admin area (two absent admin areas count as the same). When one does, Create SHALL store nothing and return that Venue's id instead, including when a concurrent Create stored it first; it SHALL NOT fail with AlreadyExists.

#### Scenario: New venue
- **WHEN** no Venue holds the place id or the listed venue name and admin area
- **THEN** the Venue is stored and its id returned

#### Scenario: Place id already held
- **WHEN** a Venue with the same place id exists
- **THEN** Create returns the existing Venue's id and stores nothing

#### Scenario: Listed name and admin area already held
- **WHEN** a Venue with listed venue name "Zepp Osaka Bayside" and admin area JP-27 exists and another is created with the same pair and a different place id
- **THEN** Create returns the existing Venue's id

#### Scenario: Same listed name, different admin area
- **WHEN** a Venue lists "Zepp" in JP-13 and another listing "Zepp" in JP-27 is created
- **THEN** a second Venue is stored

#### Scenario: Concurrent create
- **WHEN** two Creates for the same place id run at once
- **THEN** both return the id of the one Venue stored
