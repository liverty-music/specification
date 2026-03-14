## ADDED Requirements

### Requirement: Total `style` attribute ban in templates
No form of `style` attribute SHALL appear in HTML templates. Dynamic values are passed via custom attributes; static values belong in CSS files.

#### Scenario: Dynamic values via custom attributes
- **WHEN** a component needs to pass a dynamic value to CSS
- **THEN** the template SHALL use a custom attribute (e.g., `swipe-offset.bind="value"`)
- **AND** the custom attribute SHALL internally set a CSS custom property via `element.style.setProperty()`
- **AND** the template SHALL NOT contain `style=`, `style.*.bind`, or any form of `style` attribute

#### Scenario: Static inline styles prohibited
- **WHEN** a template has a `style` attribute with no dynamic binding
- **THEN** the declaration SHALL be moved to the component's CSS file
- **AND** the `style` attribute SHALL be removed

#### Scenario: Lint enforcement
- **WHEN** `make check` runs
- **THEN** a grep-based lint rule SHALL verify zero occurrences of `style` attributes in `.html` template files
- **AND** any match SHALL cause a non-zero exit code

### Requirement: `color-mix()` for dynamic alpha
Alpha/opacity variants of dynamic colors SHALL use CSS `color-mix()` instead of hex suffix concatenation.

#### Scenario: Dynamic color with alpha
- **WHEN** a component needs a semi-transparent variant of a dynamic color
- **THEN** CSS SHALL use `color-mix(in oklch, var(--_color) 25%, transparent)`
- **AND** the template SHALL NOT concatenate hex alpha suffixes (e.g., `${color}40`)

### Requirement: `translate` shorthand for transforms
Transform operations that are a single translation SHALL use the `translate` CSS property (2022 Baseline) instead of `transform: translateX/Y()`.

#### Scenario: Single-axis translation
- **WHEN** CSS applies a translation from a CSS custom property
- **THEN** the rule SHALL use `translate: var(--_x, 0) 0` or `translate: 0 var(--_y, 0)`
- **AND** the rule SHALL NOT use `transform: translateX(var(--_x))` or `transform: translateY(var(--_y))`

### Requirement: No setTimeout for CSS animation timing
TypeScript SHALL NOT use `setTimeout` with hardcoded durations that mirror CSS transition or animation durations. Animation lifecycle SHALL be driven by CSS events.

#### Scenario: Post-animation cleanup uses transitionend
- **WHEN** a component needs to perform cleanup after a CSS transition completes
- **THEN** the component SHALL listen for `transitionend` or `animationend` events
- **AND** no `setTimeout` SHALL be used with a duration value that matches a CSS duration

#### Scenario: Display duration via CSS animation
- **WHEN** a component auto-hides after a fixed display duration
- **THEN** the duration SHALL be defined in CSS (via `animation-delay` or `animation-duration`)
- **AND** the component SHALL listen for `animationend` to trigger the hide phase
- **AND** `prefers-reduced-motion` SHALL be handled via `@media` in CSS

#### Scenario: Exit animation with popover
- **WHEN** a popover element has an exit animation and needs to call `hidePopover()` after completion
- **THEN** the component SHALL listen for `animationend` on the popover element
- **AND** `hidePopover()` SHALL be called in the event handler, not in a `setTimeout` callback
