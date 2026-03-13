## ADDED Requirements

### Requirement: CSS custom properties as TS-to-CSS bridge
Dynamic values that originate in TypeScript and affect CSS layout or appearance SHALL be passed via CSS custom properties on the `style` attribute, not via inline CSS declarations.

#### Scenario: Inline style uses custom property
- **WHEN** a template binds a dynamic value to an element's style
- **THEN** the binding SHALL set a CSS custom property (e.g., `style="--_offset: ${value}px"`)
- **AND** the CSS rule SHALL consume the property (e.g., `transform: translateX(var(--_offset, 0px))`)
- **AND** the template SHALL NOT inline the full CSS declaration (e.g., `style="transform: translateX(${value}px)"`)

#### Scenario: Dynamic gradient color
- **WHEN** a component receives a dynamic color for use in a gradient
- **THEN** the template SHALL bind `style="--_color: ${color}"`
- **AND** CSS SHALL define the gradient structure using `var(--_color)`
- **AND** the template SHALL NOT construct the full `background: linear-gradient(...)` string inline

### Requirement: No setTimeout for CSS animation timing
TypeScript SHALL NOT use `setTimeout` with hardcoded durations that mirror CSS transition or animation durations. Animation lifecycle SHALL be driven by CSS events.

#### Scenario: Post-animation cleanup uses transitionend
- **WHEN** a component needs to perform cleanup after a CSS transition completes
- **THEN** the component SHALL listen for `transitionend` or `animationend` events
- **AND** no `setTimeout` SHALL be used with a duration value that matches a CSS duration

#### Scenario: Exit animation with popover
- **WHEN** a popover element has an exit animation and needs to call `hidePopover()` after completion
- **THEN** the component SHALL listen for `animationend` on the popover element
- **AND** `hidePopover()` SHALL be called in the event handler, not in a `setTimeout` callback
