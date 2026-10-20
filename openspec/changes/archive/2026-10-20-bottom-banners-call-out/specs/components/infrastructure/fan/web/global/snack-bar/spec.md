## ADDED Requirements

### Requirement: Snack bars sit above the bottom navigation and any banner

Every snack bar, whatever its severity or sender, SHALL be placed at the bottom of the screen with its bottom edge one `space-s` step above the top of the bottom navigation bar and the bottom safe-area inset. While a persistent bottom banner (the signup prompt or the install banner) is visible above the navigation bar, the snack bar SHALL sit that same step above the banner instead, using the banner's rendered height; a banner that is not visible SHALL add no height. The FAB stays sunk in the navigation bar in both cases (see FAB Menu).

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

## REMOVED Requirements

### Requirement: Snack bars sit directly above the bottom navigation

**Reason**: Replaced by "Snack bars sit above the bottom navigation and any banner": the install banner can no longer be dismissed and the FAB no longer floats above a banner, so "Install banner dismissed" becomes "A hidden banner adds no height" and "The FAB floats above a visible banner" becomes "The FAB stays sunk under a banner and a snack bar".
**Migration**: None. The other scenarios keep their names in the new requirement.
