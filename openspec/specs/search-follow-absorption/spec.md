# Search Follow Absorption

## Purpose

Defines the behavior when a user follows an artist from the search results, including the transition back to bubble view, absorption animation, and error handling.

## Requirements

### Requirement: Search result follow triggers bubble view transition and absorption animation
When a user follows an artist from the search results, the system SHALL transition back to the bubble view and play the orb absorption animation, providing the same visual feedback as a direct bubble tap.

#### Scenario: Follow from search triggers absorption
- **WHEN** a user taps a search result item for an unfollowed artist
- **THEN** the system SHALL execute the follow action (optimistic UI update)
- **AND** the system SHALL exit search mode (clear results, hide search result list)
- **AND** the system SHALL resume the bubble canvas
- **AND** the system SHALL spawn a temporary bubble at the upper area of the bubble canvas (approximately 15-20% from top)
- **AND** the system SHALL immediately start the absorption animation for that bubble toward the orb
- **AND** on absorption completion, `OrbRenderer.injectColor` SHALL be called with the bubble's hue
- **AND** the system SHALL immediately dispatch the `need-more-bubbles` custom event to trigger similar artist loading (not deferred until absorption completion)

#### Scenario: Search input is cleared after follow
- **WHEN** a user follows an artist from the search results
- **THEN** the search query input SHALL be cleared
- **AND** the search mode SHALL be deactivated

#### Scenario: Follow failure rolls back and stays in search mode
- **WHEN** a user taps a search result item
- **AND** the follow action fails (network error or backend error)
- **THEN** the system SHALL NOT exit search mode
- **AND** the system SHALL NOT spawn or absorb a bubble
- **AND** the system SHALL display an error toast notification
- **AND** the search results SHALL remain visible and interactive
