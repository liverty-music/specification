# CSS State Management

## Purpose

Defines the three-layer responsibility contract for visual state communication between TypeScript ViewModels, Aurelia templates, and CSS. TS declares state, templates pass through via binding, CSS owns all visual expression. No ternary expressions in templates, no CSS property names in HTML, no animation durations in TypeScript.

## Requirements

### Requirement: Three-layer responsibility separation
Visual state SHALL flow through three layers with strict responsibilities: TS declares state, Template binds directly, CSS owns visual expression.

#### Scenario: TS ViewModel declares state as typed values
- **WHEN** a component has visual state
- **THEN** the ViewModel SHALL expose discrete states as `string` literal unions (e.g., `state: 'active' | 'exiting'`)
- **AND** boolean states as `boolean` properties
- **AND** continuous values as `number` or `string` properties
- **AND** no state-to-string conversion SHALL be needed in the template

#### Scenario: Template passes through without transformation
- **WHEN** a template binds ViewModel state to the DOM
- **THEN** the binding SHALL be a direct passthrough (e.g., `data-state.bind="state"`)
- **AND** no ternary expressions SHALL appear in template bindings
- **AND** no string concatenation SHALL construct CSS property values in templates

### Requirement: Discrete visual state via `data-*.bind`
Components that have discrete visual states SHALL communicate state to CSS exclusively via `data-*` attributes using Aurelia's `.bind` syntax, not string interpolation.

#### Scenario: Enum state binding
- **WHEN** a component has a multi-value visual state (e.g., entering/active/exiting)
- **THEN** the ViewModel SHALL expose the state as a `string` literal union
- **AND** the template SHALL bind `data-state.bind="state"`
- **AND** CSS SHALL style via `[data-state="exiting"] { }` selectors

#### Scenario: Boolean state binding
- **WHEN** a component has a boolean visual state (e.g., active/inactive)
- **THEN** the template SHALL bind `data-active.bind="isActive"`
- **AND** Aurelia SHALL set `data-active="true"` or `data-active="false"` as string attributes
- **AND** CSS SHALL target `[data-active="true"]` for the active state
- **AND** the template SHALL NOT use `data-active.bind="expr ? '' : null"` (attribute presence/absence pattern)

#### Scenario: No string interpolation in data-* attributes
- **WHEN** a template sets a `data-*` attribute
- **THEN** the template SHALL use `.bind` syntax (e.g., `data-state.bind="state"`)
- **AND** the template SHALL NOT use interpolation syntax (e.g., `data-state="${expression}"`)

#### Scenario: Multiple orthogonal states
- **WHEN** an element has multiple independent state dimensions (e.g., variant AND disabled)
- **THEN** each dimension SHALL use a separate `data-*` attribute (`data-variant.bind="variant"`, `data-disabled.bind="isDisabled"`)
- **AND** CSS SHALL compose selectors via `[data-variant="muted"][data-disabled="true"] { }`

### Requirement: Parent container strategy for shared state flags
When multiple child elements react to the same state flag, the `data-*` attribute SHALL be placed on the nearest common parent element.

#### Scenario: Multiple children controlled by one flag
- **WHEN** two or more sibling/descendant elements change visibility or style based on the same ViewModel property
- **THEN** the `data-*` attribute SHALL be bound on the nearest common ancestor
- **AND** CSS descendant selectors SHALL control each child's visual behavior
- **AND** individual child elements SHALL NOT each receive the same `data-*` attribute

### Requirement: Total `style` attribute ban in templates
No form of `style` attribute SHALL appear in HTML templates. All visual expression is owned by CSS files.

#### Scenario: Continuous dynamic values via custom attributes
- **WHEN** a component passes a dynamic value (offset, color) from TypeScript to CSS
- **THEN** the template SHALL use a custom attribute (e.g., `swipe-offset.bind="offset"`)
- **AND** the custom attribute SHALL internally call `element.style.setProperty('--_*', value)`
- **AND** CSS SHALL consume the custom property via `var(--_*, fallback)`
- **AND** the template SHALL NOT contain `style=`, `style.*.bind`, or any `style` attribute

#### Scenario: Dynamic color via custom attribute
- **WHEN** a component receives a dynamic color value
- **THEN** the template SHALL use a custom attribute (e.g., `tile-color.bind="color"`)
- **AND** CSS SHALL use `var(--_color)` in visual declarations
- **AND** alpha/opacity variants SHALL use CSS `color-mix(in oklch, var(--_color) 25%, transparent)` instead of hex suffix hacks

#### Scenario: Component-local custom property naming
- **WHEN** a CSS custom property is scoped to a single component
- **THEN** the property name SHALL use the `--_` prefix (e.g., `--_offset`, `--_color`)
- **AND** global design token properties SHALL NOT use the `--_` prefix

#### Scenario: Static values moved to CSS
- **WHEN** a template has `style="font-size: clamp(...)"` or `style="margin-inline: auto"` with no dynamic binding
- **THEN** the declaration SHALL be moved to the component's CSS file
- **AND** the `style` attribute SHALL be removed from the template

#### Scenario: Lint enforcement
- **WHEN** `make check` runs
- **THEN** a grep-based lint rule SHALL verify zero occurrences of `style` attributes in `.html` files
- **AND** any violation SHALL fail the build

### Requirement: CSS `attr()` migration path
Custom attributes for JS→CSS bridging are a temporary measure until CSS `attr()` with `type()` coercion reaches Baseline.

#### Scenario: Future migration to CSS `attr()`
- **WHEN** CSS `attr()` with `type(<syntax>)` (CSS Values Level 5) is supported by all major browsers
- **THEN** custom attributes MAY be replaced with `data-*.bind` + CSS `attr(data-* px, fallback)` patterns
- **AND** the template binding API (e.g., `swipe-offset.bind`) SHOULD remain stable during migration

### Requirement: Animation lifecycle via CSS events
Post-animation cleanup SHALL use `transitionend` or `animationend` events instead of `setTimeout` with hardcoded durations.

#### Scenario: Exit transition cleanup
- **WHEN** a component triggers an exit transition by setting `data-state.bind` to `"exiting"`
- **THEN** the component SHALL listen for `transitionend` (filtering by `propertyName`) to perform cleanup
- **AND** no `setTimeout` SHALL be used with a duration matching the CSS transition duration

#### Scenario: Display duration via CSS animation
- **WHEN** a component needs to display content for a fixed duration before auto-hiding
- **THEN** the duration SHALL be defined via CSS `animation-delay` or `animation-duration`
- **AND** the component SHALL listen for `animationend` to trigger the next phase
- **AND** `prefers-reduced-motion` variants SHALL be handled via `@media` in CSS

#### Scenario: Reduced motion bypass
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **AND** CSS applies `transition: none` or `animation: none`
- **THEN** the component SHALL detect reduced motion via `matchMedia('(prefers-reduced-motion: reduce)')` and perform cleanup immediately

#### Scenario: Animation duration single source of truth
- **WHEN** an animation or transition duration is defined
- **THEN** the duration SHALL exist only in CSS
- **AND** no TypeScript constant (e.g., `EXIT_ANIMATION_MS`, `FADE_DURATION_MS`) SHALL duplicate the CSS duration

### Requirement: No if.bind for visual-only visibility
Elements whose visibility is managed by the Popover API or CSS transitions SHALL NOT use `if.bind` for show/hide.

#### Scenario: Popover element stays in DOM
- **WHEN** a component uses the Popover API (`showPopover()`/`hidePopover()`)
- **THEN** the popover element SHALL remain in the DOM at all times (no `if.bind`)
- **AND** the Popover API SHALL manage top-layer visibility natively

#### Scenario: Overlay with exit animation
- **WHEN** an overlay has a CSS exit transition
- **THEN** the overlay element SHALL remain in the DOM during the transition
- **AND** `if.bind` SHALL NOT remove the element before the transition completes

### Requirement: Custom attributes for JS→CSS bridge only
Custom attributes SHALL be used for passing continuous values to CSS (via `element.style.setProperty`). For discrete state, native `data-*.bind` is sufficient and custom attributes SHALL NOT be created.

#### Scenario: Custom attribute for continuous value
- **WHEN** a component needs to pass a per-frame numeric or color value to CSS
- **THEN** a custom attribute SHALL be created that internally calls `element.style.setProperty('--_*', value)`
- **AND** the custom attribute SHALL clean up (remove the property) in its `detaching` lifecycle hook

#### Scenario: No custom attribute for discrete state
- **WHEN** a template needs to set a `data-*` attribute for discrete state
- **THEN** the template SHALL use native `data-*.bind` syntax
- **AND** a custom attribute SHALL NOT be created for `data-*` passthrough bindings
