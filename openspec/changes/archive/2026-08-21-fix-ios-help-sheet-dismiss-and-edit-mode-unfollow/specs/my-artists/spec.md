## MODIFIED Requirements

### Requirement: My Artists page help content documents all available gestures

The My Artists page help content SHALL explain how to unfollow an artist via the Edit-mode
toggle. The help text SHALL communicate that activating "Edit" in the page header reveals a
per-row remove control that unfollows immediately (with Undo). The help content SHALL NOT
reference a long-press-to-unfollow gesture (that interaction is retired). Desktop-specific
interactions need not be documented in help as they are visually self-evident.

#### Scenario: Help text visible to touch device users

- **WHEN** the user opens the My Artists page help (on any device, including touch)
- **THEN** help content includes an explanation that entering Edit mode reveals a per-row remove control to unfollow an artist
- **AND** the help content SHALL NOT mention a long-press unfollow gesture

#### Scenario: Help text available in all supported locales

- **WHEN** the app is displayed in any supported locale (Japanese, English)
- **THEN** the Edit-mode unfollow help text is translated and rendered correctly
