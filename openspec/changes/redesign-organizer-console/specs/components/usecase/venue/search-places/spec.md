# Spec Delta

## Purpose

ConcertAuthoringUseCase.SearchPlaces lets an organizer operator who is authoring a concert find the venue of an event by name in the map catalog, so the event is matched to a known place instead of a free-text name.

## ADDED Requirements

### Requirement: Search for an authoring operator

SearchPlaces SHALL take the caller's Organizer and a text, SHALL fail with InvalidArgument when the text is shorter than 2 or longer than 100 characters after trimming spaces, and SHALL otherwise return the candidates of Venue.SearchPlaces unchanged. It SHALL store nothing: a Venue is created or matched only when a concert is saved with the chosen place. An Unavailable failure of Venue.SearchPlaces SHALL be returned unchanged.

#### Scenario: Operator searches a venue

- **WHEN** an operator of an active Organizer searches "LIQUIDROOM"
- **THEN** the candidates returned by Venue.SearchPlaces are returned and no Venue is stored

#### Scenario: Text too short

- **WHEN** the text is "Z"
- **THEN** SearchPlaces fails with InvalidArgument and the catalog is not called

#### Scenario: Catalog down

- **WHEN** Venue.SearchPlaces fails with Unavailable
- **THEN** SearchPlaces fails with Unavailable
