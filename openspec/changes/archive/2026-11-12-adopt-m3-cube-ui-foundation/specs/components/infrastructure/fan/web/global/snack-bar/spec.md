## MODIFIED Requirements

### Requirement: Snack bars sit above the bottom navigation and any banner

Every snack bar, whatever its severity or sender, SHALL be placed at the bottom of the screen with its bottom edge one `space-s` step above the top of the bottom navigation bar and the bottom safe-area inset. While a persistent bottom banner (the signup prompt or the install banner) is visible above the navigation bar, the snack bar SHALL sit that same step above the banner instead, using the banner's rendered height; a banner that is not visible SHALL add no height. While a screen shows a control floating over its bottom edge (the Discovery swap tile, or the Done bar of My Artists' edit mode), the snack bar SHALL sit one `space-3xs` step above that control instead, and the control SHALL NOT move; such a control always sits above any visible banner, so this placement takes precedence over the banner placement. The FAB stays sunk in the navigation bar in all cases (see FAB Menu).

#### Scenario: No banner is visible
- **WHEN** a snack bar opens and no persistent bottom banner is visible
- **THEN** the gap between the snack bar's bottom edge and the navigation bar's top edge SHALL be one `space-s` step (16 to 20px)

#### Scenario: A hidden banner adds no height
- **WHEN** a banner's host is on the screen but the banner is not visible (the app is installed, or a post-signup surface hides it)
- **AND** a snack bar opens
- **THEN** the snack bar SHALL sit one `space-s` step above the navigation bar

#### Scenario: A banner is visible
- **WHEN** a snack bar opens while the signup prompt or the install banner is visible
- **THEN** the snack bar's bottom edge SHALL sit one `space-s` step above the banner's top edge
- **AND** the snack bar SHALL NOT cover any part of the banner

#### Scenario: The FAB stays sunk under a banner and a snack bar
- **WHEN** a snack bar opens while a bottom banner is visible on a route that shows the FAB
- **THEN** the FAB SHALL stay sunk in the navigation bar
- **AND** the snack bar SHALL cover neither the FAB nor the banner

#### Scenario: Same placement for every severity
- **WHEN** an info, warning and error snack bar are each shown in turn under the same conditions
- **THEN** all three SHALL occupy the same vertical position

#### Scenario: A banner and a floating control are both visible
- **WHEN** a snack bar opens on Discovery while the install banner and the swap tile are both visible
- **THEN** the snack bar's bottom edge SHALL sit one `space-3xs` step above the swap tile's top edge
- **AND** the snack bar SHALL cover neither the swap tile nor the banner

#### Scenario: A floating control stays in place
- **WHEN** a snack bar opens on Discovery while the swap tile is shown
- **THEN** the snack bar's bottom edge SHALL sit one `space-3xs` step above the swap tile's top edge
- **AND** the swap tile SHALL stay where it was and stay tappable

#### Scenario: The Done bar of edit mode stays tappable
- **WHEN** a snack bar opens on My Artists in edit mode
- **THEN** the snack bar's bottom edge SHALL sit one `space-3xs` step above the Done bar's top edge
- **AND** a tap at the centre of the Done button SHALL reach the Done button
