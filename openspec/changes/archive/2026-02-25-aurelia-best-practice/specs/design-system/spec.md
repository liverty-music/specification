## MODIFIED Requirements

### Requirement: Design Token Definition
The system SHALL define a centralized set of design tokens using Tailwind CSS v4's `@theme` directive to ensure visual consistency across all screens.

#### Scenario: Color tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define the following color token groups via CSS custom properties:
  - `--color-brand-primary`: indigo-500
  - `--color-brand-secondary`: violet-500
  - `--color-brand-accent`: cyan-400
  - `--color-surface-background`: gray-950
  - `--color-surface-layer-1`: gray-900
  - `--color-surface-layer-2`: gray-800
  - `--color-text-primary`: white
  - `--color-text-secondary`: gray-300
  - `--color-text-muted`: gray-500
- **AND** all components SHALL reference these tokens instead of hardcoded color values

#### Scenario: Typography tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define font family tokens:
  - `--font-display`: display/heading font (e.g., Outfit) for hero copy, card headlines, section titles
  - `--font-body`: body text font (system-ui, sans-serif) for paragraphs, labels, metadata
- **AND** the system SHALL define a type scale with sizes for mega (4xl or larger), heading (2xl-3xl), body (base-lg), caption (xs-sm)

#### Scenario: Shape tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define radius tokens: `--radius-card` (1rem), `--radius-button` (0.75rem), `--radius-sheet` (1.5rem)
- **AND** the system SHALL define shadow tokens: `--shadow-card-glow`, `--shadow-sheet`, `--shadow-button`

#### Scenario: Container query breakpoint tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define container query breakpoint tokens for component-level responsive design:
  - `--container-sm`: 320px
  - `--container-md`: 480px
  - `--container-lg`: 640px
- **AND** components using Container Queries SHALL reference these tokens for consistent breakpoints

#### Scenario: View transition tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define view transition duration and easing tokens:
  - `--transition-route-duration`: 200ms
  - `--transition-route-easing`: ease-out
- **AND** route transitions SHALL reference these tokens instead of hardcoded values

## ADDED Requirements

### Requirement: View Transitions as route animation system
The design system SHALL provide View Transition styles as the primary route animation mechanism, replacing CSS keyframe animations on `au-viewport > *`.

#### Scenario: View transition styles defined
- **WHEN** the design system CSS is loaded
- **THEN** the global stylesheet SHALL define `::view-transition-old(root)` and `::view-transition-new(root)` pseudo-element styles
- **AND** the transition duration and easing SHALL use the design system tokens (`--transition-route-duration`, `--transition-route-easing`)

#### Scenario: Keyframe fallback preserved
- **WHEN** the browser does not support View Transitions
- **THEN** the existing `@keyframes page-enter` animation on `au-viewport > *` SHALL remain as a fallback
- **AND** the fallback SHALL be gated behind `@supports not (view-transition-name: x)`

### Requirement: Container Query infrastructure
The design system SHALL provide base styles for declaring container contexts.

#### Scenario: Container type utility
- **WHEN** a component needs to use Container Queries for responsive child layout
- **THEN** the component's wrapper element SHALL declare `container-type: inline-size`
- **AND** child elements SHALL use `@container` rules referencing the design system breakpoint tokens
