## MODIFIED Requirements

### Requirement: Exception layer for state deviations via `data-*` attributes
Component state variations SHALL use `data-*` attributes (not CSS class toggling) to drive styling, as enforced by the `cube/exception-data-attr` rule. Class-name ternary expressions in templates for visual state SHALL be prohibited.

#### Scenario: State-driven styling uses data attributes
- **WHEN** a component has visual state variations (e.g., active, disabled, loading)
- **THEN** the variations SHALL be expressed via `data-state`, `data-variant`, or `data-theme` attributes
- **AND** CSS selectors SHALL target `[data-state="active"]` etc. within `@layer exception` or within `@layer block` using `data-*` attribute selectors

#### Scenario: Stylelint enforces data attribute convention
- **WHEN** stylelint runs against all CSS files
- **THEN** the `cube/exception-data-attr` and `cube/data-attr-naming` rules SHALL report zero warnings

#### Scenario: Class ternary patterns prohibited for visual state
- **WHEN** a template needs to express a visual state change
- **THEN** the template SHALL NOT use `class="${condition ? 'class-name' : ''}"` patterns
- **AND** the template SHALL use `data-state="${condition ? 'active' : 'inactive'}"` or equivalent `data-*` binding instead
