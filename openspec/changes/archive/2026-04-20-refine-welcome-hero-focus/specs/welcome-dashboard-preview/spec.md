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

#### Scenario: Two-screen scroll-snap layout with hero-only Screen 1 and preview-with-CTA Screen 2

- **WHEN** the Welcome page renders with preview data
- **THEN** the page SHALL use a two-screen scroll-snap layout composed of:
  - **Screen 1 (hero)**: brand, headline, subtitle, language selector, and a single `[See how it works ↓]` scroll-affordance button — with no `[Get Started]` or `[Log In]` buttons present
  - **Screen 2 (preview + CTA)**: a contextual label, the `<concert-highway>` preview (capped at approximately 30 concerts), a fade-out gradient mask at the bottom, and the `[Get Started]` + `[Log In]` CTAs
- **AND** Screen 1 SHALL be sized so that the top edge of Screen 2 is faintly visible above the fold of the initial viewport (Screen 1 occupying approximately 95% of the small viewport height, revealing approximately 5% of Screen 2 as a peek)
- **AND** the scroll container SHALL use `scroll-snap-type: y proximity` so the viewport snaps only when the user's scroll position is near a snap point, allowing mid-scroll reading of the peek
- **AND** the user SHALL be able to scroll between screens via natural scroll gestures, with the proximity-snap providing soft alignment at the two snap points
- **AND** the system SHALL NOT render a floating arrow or icon-only scroll-hint element at any position

#### Scenario: Guest-friendly copy shown alongside preview

- **WHEN** the Welcome page renders
- **THEN** the page SHALL display the text "アカウント不要でお試しいただけます" near the CTA buttons on Screen 2

#### Scenario: Artist list is environment-configurable

- **WHEN** the application is built for a given environment
- **THEN** the curated artist UUID list SHALL be sourced from the `VITE_PREVIEW_ARTIST_IDS` environment variable (comma-separated UUIDs)
- **AND** the corresponding artist display names SHALL be sourced from the `VITE_PREVIEW_ARTIST_NAMES` environment variable (comma-separated, same order as IDs)
- **AND** all IDs in the list SHALL be valid UUIDs accepted by the `ConcertService/List` RPC
