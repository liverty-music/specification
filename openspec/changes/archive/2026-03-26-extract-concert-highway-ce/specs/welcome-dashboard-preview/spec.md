## MODIFIED Requirements

### Requirement: Live Dashboard Preview on Welcome Page

The system SHALL display an interactive, read-only dashboard preview on the Welcome page using live concert data from a curated popular-artist fallback list.

#### Scenario: Preview loads with live data via ListWithProximity RPC

- **WHEN** the Welcome page renders
- **THEN** the system SHALL call the `ListWithProximity` RPC with the curated artist UUIDs and a fixed home location of Tokyo (JP, JP-13)
- **AND** the system SHALL render the response using the `<concert-highway>` custom element in readonly mode
- **AND** concerts SHALL be correctly classified into home/nearby/away lanes by the backend's proximity calculation

#### Scenario: Fallback when artist has no concerts

- **WHEN** a curated artist has no upcoming concerts in the database
- **THEN** that artist SHALL be excluded from the preview data
- **AND** the system SHALL continue fetching from the remaining list until at least 5 artists with concerts are found

#### Scenario: Preview is read-only

- **WHEN** the user interacts with concert cards in the preview
- **THEN** tapping a card SHALL NOT navigate or open a detail sheet
- **AND** the preview SHALL serve as a visual demonstration only

#### Scenario: Full-page scroll layout with hero and preview screens

- **WHEN** the Welcome page renders with preview data
- **THEN** the page SHALL use a two-screen scroll-snap layout:
  - Screen 1 (hero): brand, headline, subtitle, CTA buttons, and language selector occupying the full viewport
  - Screen 2 (preview): a contextual label, the `<concert-highway>` preview (capped at approximately 30 concerts), a fade-out gradient mask at the bottom, and a repeated CTA footer
- **AND** the user SHALL be able to scroll between screens via scroll-snap

#### Scenario: Guest-friendly copy shown alongside preview

- **WHEN** the Welcome page renders
- **THEN** the page SHALL display the text "アカウント不要でお試しいただけます" near the CTA buttons

#### Scenario: Artist list is environment-configurable

- **WHEN** the application is built for a given environment
- **THEN** the curated artist UUID list SHALL be sourced from the `VITE_PREVIEW_ARTIST_IDS` environment variable (comma-separated UUIDs)
- **AND** the corresponding artist display names SHALL be sourced from the `VITE_PREVIEW_ARTIST_NAMES` environment variable (comma-separated, same order as IDs)
- **AND** all IDs in the list SHALL be valid UUIDs accepted by the `ConcertService/List` RPC
