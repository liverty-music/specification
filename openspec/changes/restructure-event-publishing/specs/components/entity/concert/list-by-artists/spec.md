# Spec Delta

## MODIFIED Requirements

### Requirement: Concerts of several artists, oldest first

ListByArtists SHALL return, once each, every Concert whose performers include any of the given Artists, past and upcoming, ordered by local date ascending, each with its Venue with coordinates when known. Concerts that are not visible to fans (see Concert) SHALL be left out. When none of the Artists performs anywhere, it SHALL return an empty list.

#### Scenario: Two artists
- **WHEN** Artist A performs on 2026-05-02 and Artist B on 2026-05-01
- **THEN** B's Concert is returned before A's

#### Scenario: Cancelled organizer concert excluded
- **WHEN** one of the Artists performs at a CANCELLED Event of a first-party Series
- **THEN** that Concert is not returned

#### Scenario: No concerts
- **WHEN** none of the Artists performs in any Concert
- **THEN** ListByArtists returns an empty list

#### Scenario: Draft date of a published tour excluded
- **WHEN** one of the Artists performs in a PUBLIC Series with one PUBLISHED and one DRAFT Event
- **THEN** only the PUBLISHED Event's Concert is returned
