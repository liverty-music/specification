# Spec Delta

## MODIFIED Requirements

### Requirement: Edit in the action launcher reveals per-row remove controls

The My Artists page SHALL offer an "編集" / "Edit" action in its FAB action launcher whenever at least one followed artist is listed. Choosing it SHALL put the list into edit mode and close the launcher; in edit mode each artist row SHALL display a remove (−) control as a single-tap, single-pointer affordance available on all pointer types (touch and mouse), in place of the row's hype controls, and a "完了" / "Done" bar SHALL be shown in the list. Pressing Done SHALL leave edit mode and hide the remove controls. While in edit mode the FAB action launcher SHALL NOT be shown, so neither Edit nor the Settings item of the tab pages is offered; it SHALL be shown again when edit mode ends. Edit mode SHALL NOT depend on any path-based or timed gesture (no swipe, no long-press), satisfying single-pointer operability (WCAG 2.5.1).

#### Scenario: Entering edit mode reveals remove controls

- **WHEN** the user chooses Edit in the FAB action launcher on the My Artists page
- **THEN** every artist row displays a remove (−) control in place of its hype controls
- **AND** the Done bar is shown and the launcher closes
- **AND** the FAB is not shown until the user presses Done

#### Scenario: Leaving edit mode hides remove controls

- **WHEN** the user presses Done while in edit mode
- **THEN** the remove controls are no longer displayed
- **AND** the list returns to its default presentation with hype controls

#### Scenario: Remove control is available on all pointer types

- **WHEN** the My Artists page is viewed on a touch device OR a mouse device
- **AND** edit mode is active
- **THEN** the per-row remove (−) control is visible and operable with a single tap or click
- **AND** no interaction requires a long-press or swipe gesture

#### Scenario: Default (non-editing) list shows no persistent per-row unfollow control

- **WHEN** the My Artists page loads and edit mode is NOT active
- **THEN** no persistent per-row unfollow control is shown on any pointer type, keeping the default list uncluttered
- **AND** unfollow is reachable only after entering edit mode

#### Scenario: Edit offered in the action launcher

- **WHEN** the My Artists page renders with at least one followed artist
- **THEN** the FAB action launcher offers Edit, then Help, then Settings
- **AND** the page header holds no Edit control

#### Scenario: Edit hidden when there is nothing to edit

- **WHEN** the My Artists page is loading, OR has zero followed artists (empty state)
- **THEN** Edit is not offered
- **AND** Help is still offered in the launcher

#### Scenario: Edit mode exits when the last artist is removed

- **WHEN** the user is in edit mode and removes the last remaining artist
- **THEN** the list transitions to the empty state
- **AND** edit mode is exited

#### Scenario: Edit mode is not persisted across navigation

- **WHEN** the user leaves the My Artists page while in edit mode and later returns
