## ADDED Requirements

### Requirement: Onboarding state machine diagram

The system SHALL document the onboarding state transitions as a mermaid statechart diagram, showing the linear progression through onboarding steps.

#### Scenario: Onboarding step transitions

- **WHEN** the state transition diagram is rendered
- **THEN** it SHALL show the following linear transitions:
  - `lp` → `discovery` via Get Started
  - `discovery` → `dashboard` via Generate Dashboard or Dashboard nav tap (spotlight shortcut)
  - `dashboard` → `detail` via card tapped
  - `detail` → `my-artists` via My Artists tab
  - `my-artists` → `completed` via hype level set

#### Scenario: Spotlight sub-state transitions

- **WHEN** the state transition diagram is rendered
- **THEN** it SHALL show spotlight sub-states:
  - inactive → active via `onboarding/setSpotlight`
  - active → inactive via `onboarding/clearSpotlight`

### Requirement: Guest data documentation

The system SHALL document guest data mutations as a transition table (not a state diagram, since guest state is a stateless data bag).

#### Scenario: Guest data actions

- **WHEN** the guest data documentation is rendered
- **THEN** it SHALL list the following actions with their effects:
  - `guest/follow`: append artist (idempotent, skip if exists)
  - `guest/unfollow`: remove artist by ID
  - `guest/setUserHome`: set home ISO-3166-2 code
  - `guest/clearAll`: reset follows to empty and home to null

### Requirement: Diagram location

The state transition diagrams SHALL be maintained as a spec document.

#### Scenario: Diagram file location

- **WHEN** the diagrams are created
- **THEN** they SHALL be stored in `openspec/specs/state-transition-diagram/spec.md`
- **AND** the onboarding diagram SHALL use mermaid `stateDiagram-v2` syntax
