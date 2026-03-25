# Capability: My Artists

## Purpose

Display and manage the user's followed artists, providing list and grid views with passion level controls.

## Requirements

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

#### Scenario: Hype slider replaces passion icon

- **WHEN** the My Artists list view renders
- **THEN** the system SHALL display the inline dot slider (from `hype-inline-slider` capability) instead of the passion level icon
- **AND** the bottom sheet selector SHALL NOT be used for hype changes in list view

### Requirement: Tapping passion icon opens selector (REMOVED)

**Reason**: Replaced by inline dot slider that enables 1-tap hype changes directly in the list row. The bottom sheet selector required 2 taps and interrupted the scanning flow.
**Migration**: Remove bottom sheet component usage from My Artists list view. Hype changes are handled by the inline dot slider component. The bottom sheet MAY be retained for Grid (Festival) view's long-press context menu.

### Requirement: Selecting a passion level (REMOVED)

**Reason**: The bottom sheet selection flow is replaced by inline dot slider interaction. Optimistic update and RPC call behavior moves to the slider component.
**Migration**: Optimistic update and SetHype RPC logic moves to the `hype-inline-slider` component's authenticated tap handler.

### Requirement: Hype Change Persisted for Guest Users

The system SHALL persist hype changes made by guest users to localStorage without reverting them, regardless of onboarding step.

#### Scenario: Guest user changes hype during MY_ARTISTS onboarding step

- **WHEN** a user at Step `'my-artists'` changes a hype level
- **AND** the user is not authenticated
- **THEN** the system SHALL persist the hype value in `GuestService` under `liverty:guest:hypes`
- **AND** the system SHALL NOT revert the hype change in the UI
- **AND** the system SHALL advance `onboardingStep` to `'completed'`

#### Scenario: Guest user changes hype after onboarding completion

- **WHEN** a guest user (onboarding completed) changes a hype level on the My Artists page
- **THEN** the system SHALL persist the hype value in `GuestService`
- **AND** the system SHALL NOT show a modal dialog
- **AND** the system SHALL display the guest signup banner (non-modal)

### Requirement: Hype change reverted during MY_ARTISTS step (REMOVED)

**Reason**: Reverting the user's explicitly chosen hype value immediately after they set it is confusing and contradicts the "raise your hype" coaching message. Persisting the value and merging on signup is the correct behavior.

**Migration**: Remove `artist.hype = prev` revert line in `my-artists-route.ts` `onHypeInput()`. Remove the `isOnboardingStepMyArtists` branch that triggers revert.

### Requirement: HypeNotificationDialog auto-display on unauthenticated hype change (REMOVED)

**Reason**: The dialog conflated hype explanation with account signup prompts, appearing after the user's action was silently discarded. Hype explanation is now provided upfront via PageHelp auto-open on first visit. Account promotion is handled by the non-modal signup banner.

**Migration**: Remove `showNotificationDialog = true` trigger from `onHypeInput()`. Remove `HypeNotificationDialog` component from `my-artists-route.html`. The `HypeNotificationDialog` component may be deleted.

### Requirement: View Toggle (List / Grid)

The My Artists page SHALL offer a view toggle between List view (default) and Grid (Festival) view.

#### Scenario: Toggling view mode

- **GIVEN** the My Artists page header
- **WHEN** the user taps the view toggle button
- **THEN** the page SHALL switch between List and Grid view

### Requirement: Grid (Festival) View

The Grid view SHALL display followed artists as poster-style tiles in a responsive grid layout.

#### Scenario: Away tiles are larger

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype level Away (HYPE_TYPE_AWAY)
- **THEN** their tile SHALL span 2 columns and 2 rows

#### Scenario: Non-Away tiles are standard size

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype level Watch, Home, or Nearby
- **THEN** their tile SHALL span 1 column and 1 row

#### Scenario: Long-press opens context menu

- **GIVEN** the Grid view is active
- **WHEN** the user long-presses a tile
- **THEN** a context menu SHALL appear with passion level options and an unfollow action
