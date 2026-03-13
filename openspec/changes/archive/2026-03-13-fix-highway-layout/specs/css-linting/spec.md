## MODIFIED Requirements

### Requirement: Stylelint enforces stacking context management
The linter SHALL disallow `z-index` via the `property-disallowed-list` rule. Components SHALL resolve stacking requirements through proper DOM structure — elements that need different stacking order SHALL NOT be placed as sticky siblings within the same scroll container. The `isolation: isolate` property MAY be used to scope stacking contexts where needed, but it does not substitute for correct DOM structure.

#### Scenario: No stylelint-disable for z-index
- **WHEN** stylelint runs against all CSS files
- **THEN** zero `stylelint-disable` comments for the `property-disallowed-list` rule SHALL exist
- **AND** all stacking requirements SHALL be resolved via proper DOM structure (e.g., moving fixed headers outside scroll containers)

#### Scenario: No magic numbers for sticky offsets
- **WHEN** a CSS file contains `position: sticky` with a non-zero `inset-block-start` value
- **THEN** the value SHALL reference a design token custom property
- **AND** hardcoded pixel values (e.g., `41px`) SHALL NOT be used
