# Capability: My Artists

## Purpose

Display and manage the user's followed artists, providing list and grid views with passion level controls.

## Requirements

### Requirement: Artist List Row (REMOVED)

**Reason**: The swipe-to-dismiss unfollow mechanism was abandoned due to `display: table-row` layout constraints that prevented the scroll-snap container from functioning correctly inside the artist list. Replaced by the long-press-to-unfollow flow.
**Migration**: The horizontal scroll-snap dismiss trigger is removed. Unfollow is initiated by long-pressing an artist row for ~500ms, which opens an `ArtistUnfollowSheet` confirmation bottom sheet. See `long-press-unfollow` capability spec.

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
