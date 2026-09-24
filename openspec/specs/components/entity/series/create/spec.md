# Series.Create

## Purpose

Stores one or more discovered Series with their title, type and source page.

## Requirements

### Requirement: Create stores new series once

Create SHALL store each given Series and return the ids of those it stored. A Series whose id is already stored SHALL be left unchanged — its title and source page are not overwritten — and its id SHALL NOT be returned. Repeating a Create SHALL store nothing new.

#### Scenario: New series
- **WHEN** a Series with a new id is created
- **THEN** it is stored and its id returned

#### Scenario: Existing id
- **WHEN** a Series with an already-stored id and a different title is created
- **THEN** the stored title is kept and the id is not returned

### Requirement: Create validates each series

Create SHALL fail with InvalidArgument, storing nothing, when a Series has no id, no title, or a type other than TOUR, SINGLE or FESTIVAL.

#### Scenario: Empty title
- **WHEN** one of the Series has an empty title
- **THEN** Create fails with InvalidArgument and stores nothing
