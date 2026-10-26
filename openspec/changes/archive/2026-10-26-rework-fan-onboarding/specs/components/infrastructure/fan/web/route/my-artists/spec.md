## ADDED Requirements

### Requirement: Push offer after a hype change

When a signed-in fan changes an artist's hype level on My Artists and the change is saved, My Artists SHALL show the in-app push offer as a snack, provided the fan is eligible for it and the offer limits allow it (both stated by the notification prompt surface). The snack SHALL read 「{{name}}を {{hype}} にしました。新着ライブを通知で受け取りますか？」 (EN "{{name}} is now {{hype}}. Get notified of new concerts?"), where `{{hype}}` is the invariant English tier label, with the action 「オンにする」 (EN "Turn on"). The snack SHALL stay 10 seconds unless the fan presses the action. Pressing the action SHALL show the browser's notification permission prompt at once. A guest's hype change, and a hype change whose save fails, SHALL NOT show the offer.

#### Scenario: Signed-in fan changes hype and is offered push

- **WHEN** a signed-in fan whose browser notification permission is undecided sets ヨルシカ from Nearby to Away and the change is saved
- **AND** the offer has not been shown in this session and has been left or declined fewer than 3 times
- **THEN** a snack reads 「ヨルシカを Away にしました。新着ライブを通知で受け取りますか？」 with the action 「オンにする」

#### Scenario: Pressing the action asks the browser

- **WHEN** the fan presses 「オンにする」 on the offer snack
- **THEN** the browser's notification permission prompt appears at once

#### Scenario: Guest changes hype

- **WHEN** a guest changes an artist's hype level
- **THEN** no push offer is shown

#### Scenario: Save fails

- **WHEN** a signed-in fan changes a hype level and saving fails twice
- **THEN** the failure message is shown and no push offer is shown

#### Scenario: Second hype change in the same session

- **WHEN** the fan already saw the offer in this session and changes another artist's hype level
- **THEN** the hype change applies and no push offer is shown

### Requirement: Edit in the action launcher reveals per-row remove controls

The My Artists page SHALL offer an "編集" / "Edit" action in its FAB action launcher whenever at least one followed artist is listed. Choosing it SHALL put the list into edit mode and close the launcher; in edit mode each artist row SHALL display a remove (−) control as a single-tap, single-pointer affordance available on all pointer types (touch and mouse), in place of the row's hype controls, and a "完了" / "Done" bar SHALL be shown in the list. Pressing Done SHALL leave edit mode and hide the remove controls. While in edit mode the FAB action launcher SHALL contribute no actions. Edit mode SHALL NOT depend on any path-based or timed gesture (no swipe, no long-press), satisfying single-pointer operability (WCAG 2.5.1).

#### Scenario: Entering edit mode reveals remove controls

- **WHEN** the user chooses Edit in the FAB action launcher on the My Artists page
- **THEN** every artist row displays a remove (−) control in place of its hype controls
- **AND** the Done bar is shown and the launcher closes

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
- **THEN** the FAB action launcher offers Edit next to Help
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
- **THEN** the page opens in the default (non-editing) state

## MODIFIED Requirements

### Requirement: My Artists page help content documents all available gestures

The My Artists page help content SHALL explain how to unfollow an artist via edit mode. The help text SHALL say that choosing "編集" / "Edit" in the action menu at the bottom centre (the FAB in the bottom navigation bar) reveals a per-row remove control that unfollows immediately (with Undo). The help content SHALL NOT reference a long-press-to-unfollow gesture or an Edit control in the page header. The exact help copy is stated by the page help surface ("Page-specific Help Content").

#### Scenario: Help text visible to touch device users

- **WHEN** the user opens the My Artists page help (on any device, including touch)
- **THEN** help content explains that choosing Edit in the action menu at the bottom centre reveals a per-row remove control to unfollow an artist
- **AND** the help content does not mention a long-press unfollow gesture or a header Edit control

#### Scenario: Help text available in all supported locales

- **WHEN** the app is displayed in any supported locale (Japanese, English)
- **THEN** the edit-mode unfollow help text is translated and rendered correctly

## REMOVED Requirements

### Requirement: Edit-mode toggle reveals per-row remove controls

**Reason**: Edit moved from a page-header toggle to a command in the FAB action launcher, edit mode is left with an in-list Done bar, and the hype controls give way to the remove control while editing; the old scenarios described a header toggle next to a `?` control.
**Migration**: See "Edit in the action launcher reveals per-row remove controls".
