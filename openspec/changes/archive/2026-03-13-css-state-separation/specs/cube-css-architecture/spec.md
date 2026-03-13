## MODIFIED Requirements

### Requirement: Exception layer for state deviations via `data-*` attributes
Component state variations SHALL use `data-*` attributes with Aurelia `.bind` syntax (not CSS class toggling or string interpolation) to drive styling.

#### Scenario: State-driven styling uses data-*.bind
- **WHEN** a component has visual state variations (e.g., active, disabled, loading)
- **THEN** the variations SHALL be expressed via `data-state.bind`, `data-variant.bind`, or `data-theme.bind`
- **AND** CSS selectors SHALL target `[data-state="active"]` etc. within `@layer exception` or within `@layer block` using `data-*` attribute selectors
- **AND** string interpolation (`data-state="${expr}"`) SHALL NOT be used — `.bind` is required

#### Scenario: Boolean state uses value matching
- **WHEN** a boolean state drives a visual variation
- **THEN** the template SHALL bind `data-active.bind="isActive"` (boolean passthrough)
- **AND** CSS SHALL target `[data-active="true"]` (explicit value match)
- **AND** the template SHALL NOT use `data-active.bind="expr ? '' : null"` (attribute presence/absence pattern)

#### Scenario: Parent container strategy for shared state
- **WHEN** multiple child elements react to the same state flag
- **THEN** the `data-*` attribute SHALL be bound on the nearest common ancestor
- **AND** CSS SHALL use descendant selectors (e.g., `[data-search-mode="true"] .genre-chips { display: none }`)
- **AND** child elements SHALL NOT individually carry the same `data-*` attribute

#### Scenario: Stylelint enforces data attribute convention
- **WHEN** stylelint runs against all CSS files
- **THEN** the `cube/exception-data-attr` and `cube/data-attr-naming` rules SHALL report zero warnings

#### Scenario: Class ternary patterns prohibited for visual state
- **WHEN** a template needs to express a visual state change
- **THEN** the template SHALL NOT use `class="${condition ? 'class-name' : ''}"` patterns
- **AND** the template SHALL use `data-*.bind` with a direct ViewModel value instead

#### Scenario: No ternary expressions in template bindings
- **WHEN** a template binds a value to a `data-*` attribute
- **THEN** the binding expression SHALL be a direct ViewModel property reference (e.g., `data-state.bind="state"`)
- **AND** the template SHALL NOT contain ternary expressions (e.g., `data-state.bind="flag ? 'x' : 'y'"`)
- **AND** any boolean-to-enum transformation SHALL occur in the ViewModel
