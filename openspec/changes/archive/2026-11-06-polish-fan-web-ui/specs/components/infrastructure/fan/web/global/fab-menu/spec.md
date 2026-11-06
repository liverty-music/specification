## MODIFIED Requirements

### Requirement: Per-route contextual action registration

Route components SHALL contribute their actions to the launcher when activated and
SHALL remove them when deactivated, so the launcher's contents adapt to the current
page. Re-contributing from the same owner SHALL replace that owner's previous set
(not accumulate), so a within-route state change (e.g. the end of the fan's onboarding on the dashboard, or a switch between Discovery's views) never
leaves stale items. After navigation away from a route, that route's actions SHALL
no longer appear.

#### Scenario: Dashboard contributes its actions

- **WHEN** the dashboard is displayed to a fan who is not onboarding
- **THEN** the dashboard's actions in the launcher SHALL be the beam toggle, the filter and help, followed by the Settings item (see "The launcher ends with Settings on the tab pages")

#### Scenario: Discovery contributes its actions per view

- **WHEN** Discovery shows the All Nearby view
- **THEN** Discovery's actions in the launcher SHALL be the filter and help, the filter closest to the FAB, followed by the Settings item
- **WHEN** Discovery shows the artist bubbles
- **THEN** Discovery's only action in the launcher SHALL be help, followed by the Settings item

#### Scenario: Actions removed on navigation away

- **WHEN** the user navigates from a route that contributed actions to a route that does not
- **THEN** the previous route's actions SHALL no longer appear in the launcher

#### Scenario: Within-route mode change replaces, not accumulates

- **WHEN** the fan's onboarding completes while the dashboard is displayed
- **THEN** the dashboard's actions in the launcher SHALL be the beam toggle, the filter and help, followed by the Settings item
- **AND** actions SHALL NOT be duplicated

#### Scenario: Switching Discovery's view replaces its actions

- **WHEN** the fan switches Discovery from the All Nearby view to the artist bubbles and back
- **THEN** Discovery's actions SHALL be help only on the bubbles, and the filter and help on the All Nearby view, each followed by the Settings item
- **AND** actions SHALL NOT be duplicated
