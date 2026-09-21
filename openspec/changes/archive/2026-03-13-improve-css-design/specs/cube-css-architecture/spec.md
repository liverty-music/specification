## ADDED Requirements

### Requirement: Utility layer for single-purpose overrides
The `utilities.css` file SHALL provide single-purpose utility classes that each control exactly one CSS property or concern.

#### Scenario: Animation keyframes and utility classes
- **WHEN** a component needs a shared animation
- **THEN** `@keyframes` definitions (fade-in, fade-out, fade-slide-up, modal-enter, hype-pulse, bounce-in) SHALL be defined in `@layer utility`
- **AND** corresponding `.animate-*` utility classes SHALL apply the animation with a single `animation` shorthand

#### Scenario: Reduced motion override
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** a utility-layer `@media` rule SHALL disable all animations on `.animate-*` classes and view transitions

#### Scenario: Utilities limited to single property
- **WHEN** stylelint runs against `utilities.css`
- **THEN** the `cube/utility-single-property` rule SHALL report zero warnings
