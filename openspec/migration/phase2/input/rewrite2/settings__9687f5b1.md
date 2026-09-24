<!-- spec: settings | target: components/infrastructure/fan/web/global/user-home-selector | flags: CLASSNAME | new_name: Home Area Selected-State Indicator -->
<!-- implementation names to remove: userStore -->

### Requirement: Home Area Selected-State Indicator
The home-area selector SHALL indicate the currently selected prefecture/city reactively, consistent with the language selector's selected-state treatment.

#### Scenario: Current home area is highlighted
- **WHEN** the home-area selector is open and the user has a current home area
- **THEN** the option matching `userStore.currentHome` SHALL carry a selected-state indicator (`aria-checked`/`data-selected`) bound off the observable `userStore.currentHome`
- **AND** the indicator SHALL update reactively if the current home area changes

---
