## MODIFIED Requirements

### Requirement: Sequential Lane Header Spotlight

The system SHALL introduce each dashboard lane by sequentially spotlighting the STAGE headers with explanatory coach marks. Each phase waits for a user tap **anywhere on the screen** to advance. The HOME phase pauses to collect the user's home area selection before displaying the dynamic coach mark text. Spotlight activation SHALL be deferred until concert data has loaded and the stage header elements are rendered in the DOM.

#### Scenario: HOME STAGE phase — always starts via lane intro

- **WHEN** the user is at Step `'dashboard'`
- **AND** the Dashboard page loads
- **THEN** the system SHALL always begin the lane introduction sequence (not open Home Selector directly)
- **AND** if `guest.home` or `user.home` is not yet set, the system SHALL enter the `'waiting-for-home'` sub-state within the lane intro
- **AND** the spotlight SHALL NOT be activated until concert data has loaded and the HOME STAGE header element is present in the DOM

#### Scenario: HOME STAGE phase — Home Selector conveys HOME STAGE context

- **WHEN** the lane introduction sequence begins
- **AND** `guest.home` or `user.home` is not yet set (`needsRegion` is true)
- **THEN** the system SHALL open the Home Selector bottom-sheet
- **AND** the Home Selector description text SHALL explain the HOME STAGE concept (e.g., "HOME STAGEにはあなたの地元のライブが並びます。居住エリアはどこですか？")
- **AND** the system SHALL NOT activate the coach mark spotlight (bottom-sheet and spotlight overlap on mobile)
- **AND** the HOME phase SHALL NOT advance until `onHomeSelected` fires (user selects a home area)

#### Scenario: HOME STAGE phase — spotlight activates after data load

- **WHEN** the user has selected their home area via the Home Selector
- **AND** `loadData()` has completed and `dateGroups.length > 0`
- **AND** Aurelia has rendered the stage header elements in the DOM (post-render queue flush)
- **THEN** the system SHALL activate the spotlight on `concert-highway [data-stage="home"]`
- **AND** the coach mark tooltip SHALL display the selected prefecture name with concert context
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the NEAR phase

#### Scenario: HOME STAGE phase — region already set

- **WHEN** the lane introduction sequence begins
- **AND** `guest.home` or `user.home` is already set
- **THEN** the system SHALL NOT open the Home Selector
- **AND** the system SHALL await data load completion in the `loading()` lifecycle hook
- **AND** the coach mark tooltip SHALL immediately display the prefecture-specific concert message after DOM rendering
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the NEAR phase

## REMOVED Requirements

### Requirement: HOME STAGE phase — Home Selector opens without spotlight

**Reason**: The previous scenario specified opening Home Selector "without spotlight" and without any HOME STAGE context. The HOME STAGE explanation is now conveyed via the Home Selector's own description text, avoiding the z-index overlap between bottom-sheet and coach mark spotlight on mobile.

**Migration**: Update the Home Selector i18n description text (`userHome.description`) to include HOME STAGE context. No coach mark is shown during `waiting-for-home`.
