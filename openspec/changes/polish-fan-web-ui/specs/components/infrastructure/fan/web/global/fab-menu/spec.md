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
- **THEN** the launcher SHALL present the dashboard's actions (beam toggle, filter, help)

#### Scenario: Discovery contributes its actions per view

- **WHEN** Discovery shows the All Nearby view
- **THEN** the launcher SHALL present the filter and help, the filter closest to the FAB
- **WHEN** Discovery shows the artist bubbles
- **THEN** the launcher SHALL present help only

#### Scenario: Actions removed on navigation away

- **WHEN** the user navigates from a route that contributed actions to a route that does not
- **THEN** the previous route's actions SHALL no longer appear in the launcher

#### Scenario: Within-route mode change replaces, not accumulates

- **WHEN** the fan's onboarding completes while the dashboard is displayed
- **THEN** the launcher SHALL present the beam toggle, the filter and help
- **AND** actions SHALL NOT be duplicated

#### Scenario: Switching Discovery's view replaces its actions

- **WHEN** the fan switches Discovery from the All Nearby view to the artist bubbles and back
- **THEN** the launcher SHALL present help only on the bubbles, and the filter and help on the All Nearby view
- **AND** actions SHALL NOT be duplicated
