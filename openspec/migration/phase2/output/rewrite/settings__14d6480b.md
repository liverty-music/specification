<!-- spec: settings | target: components/infrastructure/fan/web/route/settings | flags: CLASSNAME | new_name: Consent Toggle Observable Binding -->

### Requirement: Consent Toggle Observable Binding
The Settings consent toggles SHALL bind directly to the observable consent state, with no component-local mirror of that state.

#### Scenario: Consent toggles reflect service state without a mirror
- **WHEN** the Settings page renders the analytics / marketing-measurement consent toggles
- **THEN** the toggle bindings SHALL derive from the observable consent state directly
- **AND** the component SHALL NOT maintain separate mirror fields or write-back handlers for consent state

#### Scenario: External consent change updates the toggles
- **WHEN** consent state changes outside the Settings toggle handlers (e.g., via the onboarding consent screen earlier in the session)
- **THEN** the Settings toggles SHALL reflect the new state on next render without manual re-sync
