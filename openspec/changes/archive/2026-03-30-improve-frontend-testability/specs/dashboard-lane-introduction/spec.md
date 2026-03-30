## MODIFIED Requirements

### Requirement: Lane Introduction State Management
The lane introduction sequence SHALL be managed locally within the dashboard component, not persisted in the onboarding service. Nav-tab dimming SHALL be delegated to an injectable `INavDimmingService` rather than performed via direct DOM queries, enabling the state machine to be unit-tested without a real DOM.

#### Scenario: Lane intro state is ephemeral
- **WHEN** the dashboard component manages the lane introduction
- **THEN** the intro state SHALL be a local variable (`laneIntroPhase: 'home' | 'near' | 'away' | 'done'`)
- **AND** the state SHALL NOT be written to `liverty:onboardingStep` in LocalStorage

#### Scenario: Page reload during lane introduction
- **WHEN** the user reloads the page during the lane introduction sequence
- **THEN** the system SHALL restart the lane introduction from the beginning (HOME STAGE)
- **AND** the celebration overlay SHALL NOT replay (it uses a separate one-time flag)

#### Scenario: Data loading awaited before lane intro decision
- **WHEN** `startLaneIntro()` is called
- **THEN** the system SHALL await the data load response before deciding whether to run or skip the lane intro
- **AND** if the data fetch fails, the system SHALL proceed with whatever data is available (possibly empty, triggering the skip path)

#### Scenario: Nav tabs are dimmed via INavDimmingService
- **WHEN** the lane introduction starts
- **THEN** `INavDimmingService.setDimmed(true)` SHALL be called
- **AND** the component SHALL NOT directly query `[data-nav]` elements from the DOM

#### Scenario: Nav tabs are undimmed on completion or dismissal
- **WHEN** the lane introduction completes or the celebration is dismissed
- **THEN** `INavDimmingService.setDimmed(false)` SHALL be called

#### Scenario: Nav tab dimming is expressed via data attribute, not inline style
- **WHEN** `INavDimmingService.setDimmed(true)` is called on a `[data-nav]` element
- **THEN** the element SHALL receive a `data-dimmed` attribute (via `toggleAttribute`)
- **AND** the visual treatment (opacity, transition) SHALL be applied via CSS (`[data-nav][data-dimmed]` rule in the exception layer)
- **AND** no `style.setProperty` or `aria-disabled` manipulation SHALL occur
