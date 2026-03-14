## MODIFIED Requirements

### Requirement: Artist List Row

Each artist row in the My Artists list view SHALL be a horizontal scroll-snap container with the artist content and a dismiss trigger.

#### Scenario: Artist row layout

- **WHEN** an artist row is rendered in list view
- **THEN** the row SHALL be a horizontal scroll container with `scroll-snap-type: x mandatory` and hidden scrollbar
- **AND** the row content SHALL display the artist name (left) and inline dot slider (right) using `grid-template-areas: "name watch home nearby away"`
- **AND** the artist name SHALL truncate with ellipsis if it exceeds available space
- **AND** a dismiss trigger element SHALL be placed after the content as the scroll-snap end target

#### Scenario: Swipe-to-dismiss unfollows artist

- **WHEN** the user swipes an artist row left past the dismiss threshold
- **THEN** the scroll-snap SHALL snap to the dismiss-end position
- **AND** the system SHALL trigger unfollow for that artist
- **AND** if the View Transitions API is available, the remaining rows SHALL animate smoothly to fill the gap
- **AND** if the View Transitions API is unavailable, the unfollow SHALL execute immediately without animation

#### Scenario: Swipe cancel snaps back

- **WHEN** the user swipes an artist row left but does NOT pass the dismiss threshold
- **THEN** the scroll-snap SHALL snap back to the start position (content fully visible)
- **AND** no unfollow action SHALL be triggered

## REMOVED Requirements

### Requirement: Long-press unfollow in list view

**Reason**: Replaced by swipe-to-dismiss as the sole unfollow gesture in list view. Long-press added complexity (setTimeout timers, conflict with scroll) without clear UX benefit when swipe is available.
**Migration**: Remove `onLongPress`, `clearLongPressTimer`, and `LONG_PRESS_MS` from my-artists-page. Grid (Festival) view retains its own long-press context menu independently.
