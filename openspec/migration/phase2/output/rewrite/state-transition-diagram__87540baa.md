<!-- spec: state-transition-diagram | target: components/infrastructure/fan/web/global/coach-mark | flags: CLASSNAME | new_name: Coach mark is an independent, non-blocking hint -->

### Requirement: Coach mark is an independent, non-blocking hint

The coach mark SHALL be a single, transient, non-blocking hint, owned independently of onboarding state. It is activated on the discovery page when the user is in the onboarding flow and the live counts cross the threshold (5 or more followed artists, OR 3 or more followed artists with concerts), and dismissed on target tap or route detach. It SHALL NOT lock scroll or block off-target interaction, and tapping it SHALL navigate only (no state mutation).

| Action       | From       | To         |
|--------------|------------|------------|
| Activation   | `inactive` | `active`   |
| Deactivation | `active`   | `inactive` |

#### Scenario: Coach mark activates when thresholds cross

- **WHEN** the user is in the onboarding flow AND (5 or more artists are followed OR 3 or more followed artists have concerts)
- **THEN** the coach mark SHALL move from `inactive` to `active`

#### Scenario: Coach mark deactivates on tap or route detach

- **WHEN** the coach-mark target is tapped OR the route detaches
- **THEN** the coach mark SHALL move from `active` to `inactive`

#### Scenario: Coach mark does not block interaction

- **WHEN** the coach mark is `active`
- **THEN** it SHALL NOT lock scroll or block off-target interaction
- **AND** tapping it SHALL navigate only, with no onboarding-state mutation
