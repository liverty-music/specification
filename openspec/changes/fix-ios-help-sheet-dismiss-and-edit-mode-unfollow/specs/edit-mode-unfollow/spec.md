## Purpose

Provide a discoverable, accessible way to unfollow artists from the My Artists list on every pointer type: a header Edit-mode toggle that reveals a per-row remove control, replacing the retired hidden long-press gesture.

## ADDED Requirements

### Requirement: Edit-mode toggle reveals per-row remove controls

The My Artists list SHALL provide an "Edit" toggle control in the page header. Toggling it ON SHALL put the list into edit mode, in which each artist row SHALL display a remove (−) control as a single-tap, single-pointer affordance available on all pointer types (touch and mouse). Toggling it OFF SHALL leave edit mode and hide the remove controls. Edit mode SHALL NOT depend on any path-based or timed gesture (no swipe, no long-press), satisfying single-pointer operability (WCAG 2.5.1).

#### Scenario: Entering edit mode reveals remove controls

- **WHEN** the user activates the Edit toggle on the My Artists page
- **THEN** every artist row SHALL display a remove (−) control
- **AND** the Edit toggle SHALL indicate the active (editing) state

#### Scenario: Leaving edit mode hides remove controls

- **WHEN** the user deactivates the Edit toggle while in edit mode
- **THEN** the remove controls SHALL no longer be displayed
- **AND** the list SHALL return to its default (non-editing) presentation

#### Scenario: Remove control is available on all pointer types

- **WHEN** the My Artists page is viewed on a touch device (`pointer: coarse`) OR a mouse device (`pointer: fine`)
- **AND** edit mode is active
- **THEN** the per-row remove (−) control SHALL be visible and operable with a single tap or click
- **AND** no interaction SHALL require a long-press or swipe gesture

#### Scenario: Default (non-editing) list shows no persistent per-row unfollow control

- **WHEN** the My Artists page loads and edit mode is NOT active
- **THEN** no persistent per-row unfollow control SHALL be shown on any pointer type (touch or mouse), keeping the default list uncluttered
- **AND** unfollow SHALL be reachable only after entering edit mode

#### Scenario: Edit toggle presented in the page header

- **WHEN** the My Artists page renders with at least one followed artist
- **THEN** the Edit toggle SHALL be presented in the page header, on the trailing side of the page title, alongside the existing help (`?`) control

#### Scenario: Edit toggle hidden when there is nothing to edit

- **WHEN** the My Artists page is loading, OR has zero followed artists (empty state)
- **THEN** the Edit toggle SHALL NOT be shown (there is nothing to edit)
- **AND** the page title and help control SHALL still render

#### Scenario: Edit mode exits when the last artist is removed

- **WHEN** the user is in edit mode and removes the last remaining artist
- **THEN** the list SHALL transition to the empty state
- **AND** edit mode SHALL be exited (the Edit toggle returns to its non-editing label / is hidden per the previous scenario)

#### Scenario: Edit mode is not persisted across navigation

- **WHEN** the user leaves the My Artists page while in edit mode and later returns
- **THEN** the page SHALL open in the default (non-editing) state

#### Scenario: Hype controls remain usable in edit mode

- **WHEN** edit mode is active
- **THEN** the per-row hype controls SHALL remain interactive (the user can still change hype while remove controls are visible)

### Requirement: Edit-mode controls are accessible

The Edit toggle and the per-row remove controls SHALL be operable and understandable by assistive technology and keyboard users. The Edit toggle SHALL expose its pressed/active state, and each remove control SHALL have an accessible name identifying the artist it removes.

#### Scenario: Edit toggle exposes pressed state

- **WHEN** the Edit toggle is rendered
- **THEN** it SHALL be a real button operable by keyboard (Enter/Space)
- **AND** it SHALL expose its active state to assistive technology (e.g., `aria-pressed`)

#### Scenario: Remove control has an accessible name

- **WHEN** a per-row remove (−) control is shown in edit mode
- **THEN** it SHALL have an accessible name that identifies the artist to be unfollowed (e.g., "Unfollow {artist name}")
- **AND** it SHALL be operable by keyboard

### Requirement: Remove control unfollows immediately with Undo

Tapping the per-row remove (−) control in edit mode SHALL unfollow that artist immediately using the existing optimistic-removal flow, without a separate confirmation sheet, and SHALL surface an Undo affordance so the action is recoverable. Unfollow SHALL route through the existing follow-store flow (guest localStorage write or authenticated RPC) unchanged.

#### Scenario: Remove unfollows immediately

- **WHEN** the user taps the remove (−) control for an artist row in edit mode
- **THEN** the artist SHALL be removed from the list optimistically
- **AND** the unfollow SHALL be committed via the existing follow-store flow

#### Scenario: Undo restores the artist

- **WHEN** an unfollow has just been triggered via the remove control
- **AND** the user activates the Undo affordance before it expires
- **THEN** the artist SHALL be restored to the list
- **AND** the pending unfollow SHALL NOT be committed (or SHALL be reversed) consistent with the existing undo behavior

#### Scenario: Unfollow blocked during onboarding

- **WHEN** the user is still in onboarding (`OnboardingService.isOnboarding` is `true`)
- **AND** the user taps a remove control
- **THEN** the unfollow SHALL NOT execute, preserving the existing onboarding guard
