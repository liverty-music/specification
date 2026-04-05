## MODIFIED Requirements

### Requirement: My Artists page help content documents all available gestures
The My Artists page help content SHALL explain all available interactions for managing followed
artists, including the long-press-to-unfollow gesture for touch devices. The help text SHALL
communicate that long-pressing an artist row for approximately half a second opens an unfollow
confirmation dialog. Desktop-specific interactions (trash icon) need not be documented in help
as they are visually self-evident.

#### Scenario: Help text visible to touch device users
- **WHEN** user opens the My Artists page help on a touch device
- **THEN** help content includes an explanation that long-pressing an artist row opens an unfollow confirmation

#### Scenario: Help text available in all supported locales
- **WHEN** the app is displayed in any supported locale (Japanese, English)
- **THEN** the long-press unfollow help text is translated and rendered correctly
