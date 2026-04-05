## ADDED Requirements

### Requirement: Trash column hidden on touch devices
On touch-primary devices (`pointer: coarse`), the unfollow trash icon column SHALL be hidden via CSS, freeing horizontal space for the hype slider.

#### Scenario: Trash column hidden on touch device
- **WHEN** the My Artists page is rendered on a device with `pointer: coarse`
- **THEN** the trash icon column and its header SHALL NOT be visible

#### Scenario: Trash column visible on pointer device
- **WHEN** the My Artists page is rendered on a device with `pointer: fine`
- **THEN** the trash icon column SHALL remain visible and functional

#### Scenario: Row border-radius correct when trash column hidden
- **WHEN** the trash column is hidden
- **THEN** the last hype-level column cell SHALL have rounded right corners matching the card style

### Requirement: Swipe-left gesture triggers unfollow
On touch-primary devices, the user SHALL be able to swipe an artist row to the left to unfollow that artist.

#### Scenario: Swipe past threshold triggers unfollow
- **WHEN** the user swipes an artist row to the left past 40% of the row width
- **THEN** the row SHALL animate off-screen and the existing unfollow action SHALL be triggered (including undo toast)

#### Scenario: Swipe below threshold snaps back
- **WHEN** the user swipes an artist row to the left less than 40% of the row width and releases
- **THEN** the row SHALL animate back to its original position

#### Scenario: Vertical scroll is not disrupted by horizontal gesture detection
- **WHEN** the user scrolls vertically through the artist list
- **THEN** vertical scrolling SHALL work normally and SHALL NOT be intercepted as a swipe

#### Scenario: Swipe is cancelled when browser takes over scroll
- **WHEN** a swipe gesture is interrupted by the browser (e.g. momentum scroll)
- **THEN** the row SHALL immediately return to its original position without visual artifacts

### Requirement: Unfollow action remains keyboard accessible
The unfollow action SHALL remain accessible via keyboard and screen reader regardless of whether the trash column is visually hidden.

#### Scenario: Keyboard user can unfollow on touch device
- **WHEN** a keyboard user focuses the trash button (visually hidden but in DOM)
- **THEN** the button SHALL be focusable and activatable via keyboard
