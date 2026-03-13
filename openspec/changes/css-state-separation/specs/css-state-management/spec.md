# CSS State Management

## Purpose

Defines how visual state SHALL be communicated between TypeScript ViewModels and CSS stylesheets. Establishes two primitives — `data-*` attributes for discrete states and CSS custom properties for continuous values — and prohibits direct style manipulation or class toggling for visual concerns.

## Requirements

### Requirement: Discrete visual state via data-* attributes
Components that have discrete visual states (active/inactive, entering/exiting, expanded/collapsed) SHALL communicate state to CSS exclusively via `data-*` attributes on the host or target element.

#### Scenario: Component active state
- **WHEN** a component's visual state changes (e.g., active → inactive)
- **THEN** the TypeScript ViewModel SHALL set `data-state="active"` or `data-state="inactive"` on the element
- **AND** CSS SHALL style the element via `[data-state="active"] { }` selectors
- **AND** no `classList.add()`, `classList.remove()`, or `classList.toggle()` SHALL be used for visual state changes

#### Scenario: Template binding for discrete state
- **WHEN** an Aurelia template needs to express a discrete visual state
- **THEN** the template SHALL use `data-state="${expression}"` attribute binding
- **AND** the template SHALL NOT use `class="${condition ? 'name' : ''}"` ternary patterns for visual state

#### Scenario: Multiple orthogonal states
- **WHEN** an element has multiple independent state dimensions (e.g., variant AND disabled)
- **THEN** each dimension SHALL use a separate `data-*` attribute (`data-variant="muted"`, `data-disabled`)
- **AND** CSS SHALL compose selectors via `[data-variant="muted"][data-disabled] { }`

### Requirement: Continuous dynamic values via CSS custom properties
Components that need to pass dynamic numeric or color values from TypeScript to CSS SHALL use CSS custom properties via inline `style` binding, not inline style declarations.

#### Scenario: Gesture-driven transform
- **WHEN** a component tracks a gesture offset (swipe, drag) that updates per-frame
- **THEN** the template SHALL bind `style="--_offset: ${offset}px"`
- **AND** CSS SHALL apply `transform: translateX(var(--_offset, 0px))`
- **AND** the template SHALL NOT use `style="transform: translateX(${offset}px)"`

#### Scenario: Dynamic color
- **WHEN** a component receives a dynamic color value (e.g., artist theme color)
- **THEN** the template SHALL bind `style="--_color: ${color}"`
- **AND** CSS SHALL use `var(--_color)` in gradient, background, or color declarations
- **AND** the template SHALL NOT inline the full CSS declaration (e.g., `style="background: linear-gradient(...)"`)

#### Scenario: Component-local custom property naming
- **WHEN** a CSS custom property is scoped to a single component
- **THEN** the property name SHALL use the `--_` prefix (e.g., `--_offset`, `--_color`)
- **AND** global design token properties SHALL NOT use the `--_` prefix

### Requirement: Animation lifecycle via CSS events
Post-animation cleanup (DOM removal, state reset, callback invocation) SHALL use `transitionend` or `animationend` events instead of `setTimeout` with hardcoded durations.

#### Scenario: Exit transition cleanup
- **WHEN** a component triggers an exit transition by setting `data-state="exiting"`
- **THEN** the component SHALL listen for `transitionend` (filtering by `propertyName`) to perform cleanup
- **AND** no `setTimeout` SHALL be used with a duration matching the CSS transition duration

#### Scenario: Reduced motion bypass
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **AND** CSS applies `transition: none` or `animation: none`
- **THEN** the component SHALL detect reduced motion via `matchMedia('(prefers-reduced-motion: reduce)')` and perform cleanup immediately
- **AND** the component SHALL NOT wait for `transitionend` (which will not fire)

#### Scenario: Animation duration single source of truth
- **WHEN** an animation or transition duration is defined
- **THEN** the duration SHALL exist only in CSS (via design token or direct value)
- **AND** no TypeScript constant (e.g., `EXIT_ANIMATION_MS`, `FADE_DURATION_MS`) SHALL duplicate the CSS duration

### Requirement: No if.bind for visual-only visibility
Elements whose visibility is managed by the Popover API or CSS transitions SHALL NOT use `if.bind` for show/hide. DOM insertion/removal SHALL be reserved for conditional content, not visual state.

#### Scenario: Popover element stays in DOM
- **WHEN** a component uses the Popover API (`showPopover()`/`hidePopover()`)
- **THEN** the popover element SHALL remain in the DOM at all times (no `if.bind`)
- **AND** the Popover API SHALL manage top-layer visibility natively

#### Scenario: Overlay with exit animation
- **WHEN** an overlay has a CSS exit transition (e.g., fade out)
- **THEN** the overlay element SHALL remain in the DOM during the transition
- **AND** `if.bind` SHALL NOT remove the element before the transition completes
- **AND** element removal (if needed) SHALL happen in the `transitionend` callback

### Requirement: Aurelia custom attribute for state binding
A reusable Aurelia custom attribute SHALL provide declarative data-state binding, eliminating repetitive ternary expressions in templates.

#### Scenario: Boolean state binding
- **WHEN** a component has a boolean property that drives a visual state
- **THEN** the template MAY use `<div data-active.bind="isActive">` to set or remove the `data-active` attribute
- **AND** CSS SHALL target `[data-active]` for the active state and `:not([data-active])` for the inactive state
