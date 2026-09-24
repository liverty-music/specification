<!-- spec: state-transition-diagram | target: components/infrastructure/fan/web/global/coach-mark | flags: CLASSNAME | new_name: Coach mark is an independent, non-blocking hint -->

### Requirement: Coach mark is an independent, non-blocking hint

The coach mark SHALL be a single, transient, non-blocking hint owned by `CoachMarkService`, separate from onboarding state. It is activated from `DiscoveryRoute` when `isOnboarding` is true and the live counts cross the threshold (`followedCount >= 5` OR `artistsWithConcertsCount >= 3`), and dismissed on target tap or route detach. It SHALL NOT lock scroll or block off-target interaction, and tapping it SHALL navigate only (no state mutation).

| Action                        | From       | To         |
|-------------------------------|------------|------------|
| `CoachMarkService.activate`   | `inactive` | `active`   |
| `CoachMarkService.deactivate` | `active`   | `inactive` |

#### Scenario: Coach mark activates when thresholds cross

- **WHEN** `isOnboarding` is true AND (`followedCount >= 5` OR `artistsWithConcertsCount >= 3`)
- **THEN** `CoachMarkService.activate` SHALL move the coach mark from `inactive` to `active`

#### Scenario: Coach mark deactivates on tap or route detach

- **WHEN** the coach-mark target is tapped OR the route detaches
- **THEN** `CoachMarkService.deactivate` SHALL move it from `active` to `inactive`

#### Scenario: Coach mark does not block interaction

- **WHEN** the coach mark is `active`
- **THEN** it SHALL NOT lock scroll or block off-target interaction
- **AND** tapping it SHALL navigate only, with no onboarding-state mutation
