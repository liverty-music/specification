## MODIFIED Requirements

### Requirement: Live Dashboard Preview on Welcome Page

The system SHALL display an interactive, read-only dashboard preview on the Welcome page using live concert data from a curated popular-artist fallback list.

#### Scenario: Preview loads with live data

- **WHEN** the Welcome page renders
- **THEN** the system SHALL fetch concert data for a curated list of popular Japanese artists (e.g., Mrs. GREEN APPLE, YOASOBI, Vaundy, SUPER BEAVER, King Gnu, Official髭男dism, and others — at least 10 artists, excluding Ano)
- **AND** the system SHALL display the real dashboard lane component with the fetched data
- **AND** the preview SHALL be scrollable

#### Scenario: Fallback when artist has no concerts

- **WHEN** a curated artist has no upcoming concerts in the database
- **THEN** that artist SHALL be excluded from the preview data
- **AND** the system SHALL continue fetching from the remaining list until at least 5 artists with concerts are found

#### Scenario: Preview is read-only

- **WHEN** the user interacts with concert cards in the preview
- **THEN** tapping a card SHALL NOT navigate or open a detail sheet
- **AND** the preview SHALL serve as a visual demonstration only

#### Scenario: Guest-friendly copy shown alongside preview

- **WHEN** the Welcome page renders
- **THEN** the page SHALL display the text "アカウント不要でお試しいただけます" near the CTA buttons

#### Scenario: Artist list is environment-configurable

- **WHEN** the application is built for a given environment
- **THEN** the curated artist UUID list SHALL be sourced from the `VITE_PREVIEW_ARTIST_IDS` environment variable (comma-separated UUIDs)
- **AND** all IDs in the list SHALL be valid UUIDs accepted by the `ConcertService/List` RPC
