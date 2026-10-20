## ADDED Requirements

### Requirement: Route content ends above a bottom banner

While a persistent bottom banner (the signup prompt or the install banner) is visible, the area in which routes render SHALL end at the banner's top edge instead of the navigation bar's, so that no route content lies under the banner. Routes SHALL NOT compensate for the banner themselves. While no banner is visible, the area SHALL end at the navigation bar as before.

#### Scenario: Last row clears the banner
- **WHEN** a signed-in fan scrolls Settings to its end while the install banner is visible
- **THEN** the Sign out row SHALL lie entirely above the banner's top edge
- **AND** a tap at the row's centre SHALL reach the row, not the banner

#### Scenario: Empty state clears the banner and the FAB
- **WHEN** a guest with no followed artists opens My Artists while the signup prompt is visible
- **THEN** the empty state's button SHALL lie entirely above the banner's top edge
- **AND** a tap at the button's centre SHALL reach the button, not the banner or the FAB

#### Scenario: No banner, no reserved space
- **WHEN** no bottom banner is visible
- **THEN** the route area SHALL end at the navigation bar's top edge
